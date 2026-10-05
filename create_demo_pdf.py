"""Generate a demo screenplay PDF for CineForge testing.

This screenplay includes a deliberate scheduling conflict:
- Sarah is only available until 17:00 on Day 1
- Scene 7 requires Sarah and is intentionally positioned to be scheduled late

Run this script to generate sample_data/demo_screenplay.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def create_demo_screenplay():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "demo_screenplay.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1.5 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles for screenplay format
    title_style = ParagraphStyle(
        "ScreenplayTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    author_style = ParagraphStyle(
        "Author",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=36,
    )

    scene_heading = ParagraphStyle(
        "SceneHeading",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier-Bold",
        spaceBefore=24,
        spaceAfter=12,
        textTransform="uppercase",
    )

    action_style = ParagraphStyle(
        "Action",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier",
        spaceAfter=12,
        leading=14,
    )

    character_style = ParagraphStyle(
        "Character",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier-Bold",
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=0,
    )

    dialogue_style = ParagraphStyle(
        "Dialogue",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier",
        leftIndent=1 * inch,
        rightIndent=1 * inch,
        spaceAfter=12,
        leading=14,
    )

    parenthetical_style = ParagraphStyle(
        "Parenthetical",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier",
        leftIndent=1.2 * inch,
        rightIndent=1.2 * inch,
        spaceAfter=0,
    )

    transition_style = ParagraphStyle(
        "Transition",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Courier-Bold",
        alignment=TA_RIGHT,
        spaceBefore=12,
        spaceAfter=12,
    )

    story = []

    # Title Page
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("THE LAST TRAIN", title_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Written by", author_style))
    story.append(Paragraph("CineForge Demo", author_style))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SCENE 1 — Coffee Shop, Morning
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. COFFEE SHOP - MORNING", scene_heading))
    story.append(Paragraph(
        "A warm, busy coffee shop in downtown Mumbai. Morning light streams through large windows. "
        "The place is half-full with office workers getting their morning fix.",
        action_style
    ))
    story.append(Paragraph(
        "SARAH (28, sharp-eyed journalist, always carrying a worn leather notebook) "
        "sits at a corner table, nursing a black coffee. She checks her phone anxiously.",
        action_style
    ))
    story.append(Paragraph(
        "RAHUL (32, quiet software engineer, glasses, perpetually disheveled) "
        "enters and scans the room. He spots Sarah and walks over.",
        action_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph("(hesitant)", parenthetical_style))
    story.append(Paragraph("Sarah? I got your message. What's so urgent?", dialogue_style))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "Sit down. I found something. About the Westline Railway shutdown.",
        dialogue_style
    ))
    story.append(Paragraph(
        "She slides her notebook across the table. Rahul picks it up, reads, and his expression changes.",
        action_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph("This can't be real. These are internal memos.", dialogue_style))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "They're real. And if we don't move fast, everything gets buried.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 2 — Rahul's Apartment, Night
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. RAHUL'S APARTMENT - NIGHT", scene_heading))
    story.append(Paragraph(
        "A cramped one-bedroom apartment filled with computer monitors and stacks of old newspapers. "
        "Code scrolls across two screens.",
        action_style
    ))
    story.append(Paragraph(
        "Rahul sits at his desk, typing furiously. His phone buzzes. He ignores it.",
        action_style
    ))
    story.append(Paragraph(
        "On screen: a database query returning hundreds of financial records.",
        action_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph("(to himself)", parenthetical_style))
    story.append(Paragraph("There it is. Follow the money.", dialogue_style))
    story.append(Paragraph(
        "He grabs his phone and calls Sarah.",
        action_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph(
        "Sarah, I found the account. The transfers match. We need to talk to Meera.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 3 — Coffee Shop, Afternoon (same location as Scene 1)
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. COFFEE SHOP - AFTERNOON", scene_heading))
    story.append(Paragraph(
        "The same coffee shop, now quieter. Afternoon sun casts long shadows.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah meets MEERA (45, railway union leader, weathered face, strong presence). "
        "They sit across from each other, tension palpable.",
        action_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "Meera, the documents show someone inside the railway board approved the shutdown "
        "knowing it would displace 50,000 commuters. Was it you?",
        dialogue_style
    ))
    story.append(Paragraph("MEERA", character_style))
    story.append(Paragraph("(controlled anger)", parenthetical_style))
    story.append(Paragraph(
        "I fought against that shutdown for three years. They went over my head.",
        dialogue_style
    ))
    story.append(Paragraph(
        "Meera pulls out a thick folder from her bag and places it on the table.",
        action_style
    ))
    story.append(Paragraph("MEERA", character_style))
    story.append(Paragraph(
        "Here. Everything I have. Names, dates, approvals. Use it.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 4 — Train Platform, Evening
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("EXT. WESTLINE TRAIN PLATFORM - EVENING", scene_heading))
    story.append(Paragraph(
        "A deserted, aging train platform on the Westline route. Graffiti covers the walls. "
        "A single flickering fluorescent light illuminates the empty tracks. "
        "The platform is eerily quiet.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah walks along the platform alone, recording a voice memo on her phone. "
        "She photographs the abandoned ticket counter and the faded timetable.",
        action_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph("(into phone)", parenthetical_style))
    story.append(Paragraph(
        "Westline Platform 3. October 15th. The last train ran six months ago. "
        "50,000 daily commuters displaced. And nobody asked them.",
        dialogue_style
    ))
    story.append(Paragraph(
        "A distant train horn echoes. Sarah looks down the tracks into the darkness.",
        action_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 5 — Newsroom, Morning
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. NEWSROOM - MORNING", scene_heading))
    story.append(Paragraph(
        "A bustling newspaper office. Phones ring, keyboards clatter. "
        "Newsprint and coffee cups cover every surface.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah stands before VIKRAM (55, editor-in-chief, silver-haired, authoritative), "
        "presenting documents spread across his desk.",
        action_style
    ))
    story.append(Paragraph("VIKRAM", character_style))
    story.append(Paragraph(
        "Sarah, this implicates the transport minister. You understand what that means?",
        dialogue_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "I understand it means we do our job. I have sources, documents, financial trails.",
        dialogue_style
    ))
    story.append(Paragraph("VIKRAM", character_style))
    story.append(Paragraph("(long pause)", parenthetical_style))
    story.append(Paragraph(
        "You have 48 hours. Get me one more source. Then we run it.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 6 — Street Outside Newsroom, Morning
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("EXT. STREET OUTSIDE NEWSROOM - MORNING", scene_heading))
    story.append(Paragraph(
        "Sarah exits the newsroom building and walks quickly down a crowded street. "
        "She pulls out her phone.",
        action_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph("(on phone)", parenthetical_style))
    story.append(Paragraph(
        "Rahul, Vikram gave us 48 hours. We need to find Kumar before they do.",
        dialogue_style
    ))
    story.append(Paragraph(
        "She hails an auto-rickshaw and jumps in.",
        action_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 7 — Rahul's Apartment, Evening (DELIBERATE CONFLICT SCENE)
    # This scene requires Sarah AND Rahul, and is meant to be
    # scheduled late in the day to trigger the actor conflict
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. RAHUL'S APARTMENT - EVENING", scene_heading))
    story.append(Paragraph(
        "Rahul's apartment, later that evening. Multiple monitors glow in the darkness. "
        "Documents and printouts cover every surface.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah arrives, visibly tense. Rahul has a breakthrough on his screen.",
        action_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph(
        "I traced the shell companies. They all lead back to one person. "
        "Deputy Minister Kumar's brother-in-law.",
        dialogue_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "Can you prove it? Beyond the financial records?",
        dialogue_style
    ))
    story.append(Paragraph("RAHUL", character_style))
    story.append(Paragraph(
        "I have server logs, email metadata, and three corroborating transactions.",
        dialogue_style
    ))
    story.append(Paragraph(
        "Sarah stares at the screen, then at the documents on the wall. "
        "She picks up her notebook and begins writing furiously.",
        action_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "We go to Meera's contact first thing tomorrow.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 8 — Train Station Interior, Afternoon
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. CENTRAL TRAIN STATION - AFTERNOON", scene_heading))
    story.append(Paragraph(
        "The grand central station, massive and echoing. Crowds of commuters rush past.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah and Meera walk side by side through the main hall. "
        "Meera points to a departures board.",
        action_style
    ))
    story.append(Paragraph("MEERA", character_style))
    story.append(Paragraph(
        "See that? Every route that was 'unprofitable' was serving working-class neighborhoods. "
        "The profitable routes to the new tech parks? All expanded.",
        dialogue_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "Transportation as class warfare.",
        dialogue_style
    ))
    story.append(Paragraph("MEERA", character_style))
    story.append(Paragraph(
        "Not warfare. Erasure. You erase the route, you erase the community.",
        dialogue_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 9 — Newsroom, Night (Climax)
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("INT. NEWSROOM - NIGHT", scene_heading))
    story.append(Paragraph(
        "The newsroom is nearly empty. Just Sarah, Rahul, and Vikram remain. "
        "The story is laid out across Vikram's desk.",
        action_style
    ))
    story.append(Paragraph("VIKRAM", character_style))
    story.append(Paragraph("(reading)", parenthetical_style))
    story.append(Paragraph(
        "This is solid. Financial trail, three sources, documentary evidence.",
        dialogue_style
    ))
    story.append(Paragraph("SARAH", character_style))
    story.append(Paragraph(
        "Meera's contact at the railway board confirmed everything. On the record.",
        dialogue_style
    ))
    story.append(Paragraph("VIKRAM", character_style))
    story.append(Paragraph(
        "We run it. Front page. Tomorrow morning.",
        dialogue_style
    ))
    story.append(Paragraph(
        "Sarah and Rahul exchange a look. Relief. Exhaustion. Purpose.",
        action_style
    ))
    story.append(Paragraph("CUT TO:", transition_style))

    # ═══════════════════════════════════════════════════════════════
    # SCENE 10 — Train Platform, Dawn (Final Scene)
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("EXT. WESTLINE TRAIN PLATFORM - DAWN", scene_heading))
    story.append(Paragraph(
        "The same deserted platform from Scene 4. First light. "
        "Sarah stands alone on the platform, newspaper in hand. "
        "The front page headline reads: 'WESTLINE SHUTDOWN: THE HIDDEN BILLIONS.'",
        action_style
    ))
    story.append(Paragraph(
        "She folds the newspaper and places it on the empty bench. "
        "In the distance, the faint sound of a train horn.",
        action_style
    ))
    story.append(Paragraph(
        "Sarah smiles. She turns and walks away.",
        action_style
    ))
    story.append(Paragraph("FADE OUT.", transition_style))
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("THE END", title_style))

    doc.build(story)
    print(f"Demo screenplay created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_demo_screenplay()
