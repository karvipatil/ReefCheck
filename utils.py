from PIL import Image, ExifTags
import pandas as pd
from collections import defaultdict
import xlsxwriter 


def handle_image_orientation(image):

    """

    Handling image orientation
    
    Arguments:
        image: PIL image

    Outputs:
        image: oriented PIL image

    """

    try:
        # checks orientation of image, otherwise jumps out
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        # gets numeric info about orientation
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)

        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)

        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):

        print("Image does not have exif data")
        # cases: image don't have exif data
        pass

    return image


    # Image utilities


# substrate analysis

def generate_keys(key_list, multiplier = 3):
    
    """
    Generating keys
    
    """
    new_list = []
    for label in key_list:
        new_list.extend([label]*multiplier)
    return new_list

def create_substrate_dataframe(response_data: dict, csv_name: str) -> pd.DataFrame:
    """
    Creating a dataframe using the LLM output
    
    Args: response_data, csv_name
    Output: Dataframe (df)

    
    """
    segment_distances = ["0 - 19.5m", "25 - 44.5m", "50 - 65.5m", "75 - 94.5m"]
    # get unique keys
    response_keys = list(response_data.keys())
    # create dataframes
    df = pd.concat([pd.DataFrame.from_dict(response_data[key]) for key in list(response_data.keys())], axis = 1)
    # create unique column names
    column_names = []
    for num in range(len(list(response_data.keys()))):
        column_names.extend([f"distance_{num}", f"label_{num}", f"clear_{num}"])
    # set column names
    df.columns = column_names
    segment_list = generate_keys(list(response_data.keys()))
    merge_list = generate_keys(segment_distances)
    arrays = [
        segment_list,
        merge_list,
        column_names
    ]
    columns = pd.MultiIndex.from_arrays(arrays)
    df = pd.DataFrame(df.iloc[:,:].values, columns=columns)
    df.to_csv(csv_name, index=False)
    return df



def extract_data_from_dataframe(df):
    """
   Extracts data from the dataframe
   
   Args: pandas dataframe

   Outputs: dict segment info: distance, label, label_status

    Example:
    {'segment_one': [{'distance': '0.0', 'label': 'HC', 'label_status': True}, 
    {'distance': '0.5', 'label': 'HC', 'label_status': True}, 
    {'distance': '1.0', 'label': 'HC', 'label_status': True}, 
                    ... ],
    'segment_two': [{'distance': '25.0', 'label': 'HC', 'label_status': True}, 
    {'distance': '25.5.5', 'label': 'HC', 'label_status': True}, 
    {'distance': '26.0', 'label': 'HC', 'label_status': True}, 
                    ... ],

    ...

}
    
    
    """
    suffixes = ["one", "two", "three", "four"]
    segment_info = defaultdict(list)
    columns_df = list(df.columns)
    count = 0

    for index in range(0, 12, 3):
        distances = df[columns_df[index]].to_list()
        labels = df[columns_df[index+1]].to_list()
        statuses = df[columns_df[index+2]].to_list()
        segment_name = f"segment_{suffixes[count]}"
        
        for distance_, label_, status_ in zip(distances, labels, statuses):
            segment_info[segment_name].append({
                "distance": distance_,
                "label": label_,
                "label_status": status_
            })
        count += 1

    return dict(segment_info)



def extract_details(info: dict) -> list:
    return [info["distance"], info["label"], info["label_status"]]



def extract_single_attributes(selected_set: list, index_val: int) -> list:
    sub_segments = []
    # first segment
    first_set = selected_set[index_val]
    second_set = selected_set[index_val + 20]
    sub_segments.extend(extract_details(first_set))
    sub_segments.extend(extract_details(second_set))
    return sub_segments



# excel creation

def create_substrate_excel_file(substrate_dict: dict, excel_file_name: str):
  segment_set_1 = substrate_dict["segment_one"]
  segment_set_2 = substrate_dict["segment_two"]
  segment_set_3 = substrate_dict["segment_three"]
  segment_set_4 = substrate_dict["segment_four"]

  final_segments = []
  for index in range(20):
        sub_set_segments = []
        # first segment
        sub_set_segments.extend(extract_single_attributes(segment_set_1, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(segment_set_2, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(segment_set_3, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(segment_set_4, index))
        # append the segment
        final_segments.append(sub_set_segments)

  # creating workbook and worksheet

  workbook = xlsxwriter.Workbook(excel_file_name)
  worksheet = workbook.add_worksheet()


  # bolding the borders of cells
  bold = workbook.add_format({"bold": True, "border": True, "center_across": True})
  # making the background red for unclear labels
  not_clear = workbook.add_format({"bold": True, "bg_color": "red", "border": True})
  # adding borders for cells
  borders = workbook.add_format({"border": True})

  # adjusting the columns
  worksheet.merge_range("A1:P1", "Substrate Information", bold)
  worksheet.merge_range("A2:D2", "Segment_one", bold)
  worksheet.merge_range("E2:H2", "Segment_two", bold)
  worksheet.merge_range("I2:L2", "Segment_three", bold)
  worksheet.merge_range("M2:P2", "Segment_four", bold)

  # distances
  worksheet.merge_range("A3:D3", "0 - 19.5 m", bold)
  worksheet.merge_range("E3:H3", "25 - 44.5 m", bold)
  worksheet.merge_range("I3:L3", "50 - 69.5 m", bold)
  worksheet.merge_range("M3:P3", "75 - 94.5 m", bold)


  row = 3
  for segment in final_segments:
    col = 0
    for ridx in range(0, 24, 3):
      worksheet.write(row, col, segment[ridx], borders)
      col += 1
      worksheet.write(row, col, segment[ridx+1], not_clear if not segment[ridx+2] else borders)
      col += 1
    row += 1
  workbook.close()




















