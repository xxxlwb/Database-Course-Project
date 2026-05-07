from typing import List

def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    """Naive paragraph-aware chunker."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: List[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf:
                out.append(buf)
            if len(p) <= max_chars:
                buf = p
            else:
                # split overly long paragraph
                for i in range(0, len(p), max_chars):
                    out.append(p[i:i + max_chars])
                buf = ""
    if buf:
        out.append(buf)
    return out
