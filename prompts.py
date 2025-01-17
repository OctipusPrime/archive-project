README_PROMPT = """
You're a professional and experienced web developer and open source contributor. Create a first release README document for these files. The target audience is professional developers with five years of experience building python projects.

- Include a description
- A list of interesting techniques the code uses in the files provided. 
- A list of non-obvious technologies or libraries used in the code that would be of interest to professional developers with medium level experience.
- A breakdown of the project structure as a directory list code block: Include directories like any images directories or subfolders implied by the code, but not individual files unless they're in the root directory. Add a short description of any interesting directories underneath the code block
- If you mention a file or directory in the description, link to the file using relative links assuming you're in the root directory of the repo.
- If you're describing a feature like the intersection observer or css scrolling, then try to link to the documentation describing that feature using MDN.
- I don't need a How to Use section

Avoid using verbose, indirect, or jargon-heavy phrases. Opt for straightforward, concise, and conversational language that is accessible and engaging to a broad audience. Strive for simplicity, clarity, and directness in your phrasing. It should directly engage the audience. Use a matter-of-fact tone, with fewer adjectives and a more straightforward approach. Please remain neutral.
"""