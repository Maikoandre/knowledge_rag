from docling.document_converter import DocumentConverter

source = "docs/One Call API_ 2.5.html"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
with open("output.md", "w") as f:
    f.write(result.document.export_to_markdown())
# print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"