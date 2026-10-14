"""Step 1 logic: raw Project Gutenberg text -> clean running text."""
import re

START_MARKER = "*** START OF THE PROJECT GUTENBERG EBOOK"
END_MARKER = "*** END OF THE PROJECT GUTENBERG EBOOK"
FIRST_CHAPTER = re.compile(r"^I\.\s*$", re.MULTILINE)   # "I." on a line of its own
CHAPTER_HEADING = re.compile(r"^(?:I|II|III)\.\s*$", re.MULTILINE)


def clean(raw: str) -> str:
    """Remove everything that is not the story itself.

    1. unify line endings (the file has Windows CRLF)
    2. cut the Gutenberg licence header and footer
    3. cut the title page (it lists letter-spaced words that would pollute the count)
    4. drop the chapter numbers (I., II., III.)
    5. replace dashes and guillemets with spaces, collapse all whitespace
    """
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    start = text.index(START_MARKER)
    text = text[text.index("\n", start) + 1:]
    text = text[:text.index(END_MARKER)]

    first = FIRST_CHAPTER.search(text)
    if first:
        text = text[first.start():]
    text = CHAPTER_HEADING.sub(" ", text)

    text = re.sub(r"--|[»«]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
