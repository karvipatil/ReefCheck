SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS = r"""

You will see a photo of a slate containing ReefCheck information

It contains 4 distance segments as columns, with a list of substrate observations.

There are rows within the segments containing distances and their substrate observations.


Explanation of the content:

1. The distance is measured in meters, and they are numeric values (example: 0, 0.5, 1, 62.5, 72, 25)

2. Substrate symbols: HC, NIA, RB, OT, SC, SP, SD, RKC, RC, SI

3. HC = hard coral, NIA = nutrient indicator algae, RB = rubble, OT = other, SC = soft coral, SP = sponge, SD = sand, RKC = recently killed coral, RC = rock, SI = silt/clay

4. Substrate symbols may cover multiple distance values. In this case, the substrate should be mapped to each value covered.



You need to extract:

1.  every distance numeric value from the leftmost columns (example: 0, 0.5, 1, 25, 25.5)

2. The labels for each distance numeric value (example: RC, HC, OT, RB)

3. If the labels are clearly visible and readable, set label_status True. If the labels are not clearly visible or readable, or you had to guess it, set label_status False.



Rule for checking no label:

1. If the substrate box is empty or kept blank, there is no label. Also set label_status False

2. If there is a slash (/, \), there is no label. Also set label_status False

3. If there is a cross (x, X), there is no label. Also set label_status False

4. If there is a hyphen (-, _), there is no label. Also set label_status False

5. If "No info" is written (example: N/A, no information), there is no label. Also set label_status False.



Segment Information:

1. Segment 1 contains 40 pairs of distance values and substrates, starting distance values from 0 and going to 19.5.

2. Segment 2 contains 40 pairs of distance values and substrates, starting distance values from 25 and going to 44.5.

3. Segment 3 contains 40 pairs of distance values and substrates, starting distance values from 50 and going to 69.5.

4. Segment 4 contains 40 pairs of distance values and substrates, starting distance values from 75 and going to 94.5.


Guessing rule:

Guess only if you see shapes that resemble letters/numbers of a substrate code but they are smudged or incomplete; then set label_status=false
List the distance values and substrate symbols



List the distance values as "distance", substrate symbols as "label", and label_status in the following format:

{"distance": 0.0,  "label": "HC",       "label_status": true}

{"distance": 0.5,  "label": "no_label", "label_status": true}

{"distance": 1.0,  "label": "RB",       "label_status": false}


"""


FISH_SLATE_IMAGE_INSTRUCTIONS = r"""
You will be shown a photo of a diver’s tally sheet.

Input image: Image of the recordings

Rotate the slate 90 degrees clockwise so headers read left-to-right.

Depth rows (exact text): 0–20 m (distance_one) · 25–45 m (distance_two) · 50–70 m (distance_three) · 75–95 m (distance_four)

For every species name below, inspect the cell at each depth and report:  
• count – integer you see (digits are normally circled)  
• *_clear – true if the numeral is crisp; false if faint, smudged or partly erased  
• If the cell is totally blank write count 0 and *_clear true.

Treat a circled “S” as the digit 5.

Return **one JSON object** that matches the Pydantic model shown after

the species list.  Do not add any other keys or text.

Species list (verbatim)  
Fish – Butterflyfish · Sweetlips · Snapper · Barramundi cod · Humphead wrasse · Bumphead parrotfish · Other parrotfish · Moray eel · Grouper 30-40 cm · Grouper 40-50 cm · Grouper 50-60 cm · Grouper > 60 cm  
Invertebrates – Banded coral shrimp · Diadema urchin · Pencil urchin · Collector urchin · Sea cucumber · Crown of Thorns · Triton · Lobster · Giant Clam < 10 cm · Giant Clam 10-20 cm · Giant Clam 20-30 cm · Giant Clam 30-40 cm · Giant Clam 40-50 cm · Giant Clam > 50 cm  
Impacts – Coral Damage – boat/anchor · Coral Damage – dynamite · Coral Damage – other · Trash – fish nets · Trash – general · Bleaching % population · Bleaching % colony  
Coral Disease – Black Band % colonies · White band % colonies  
Rare Animals – Shark · Turtle · Manta · Other
"""










