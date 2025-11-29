# Augmented PDF Parser
Based on package: __pypdfium2__

## Introduction
This module converts PDF files into structured JSON files, making it easier to build RAG (Retrieval-Augmented Generation) systems when your manuals or knowledge base are in PDF format.

## How It Works
PDF files contain a TOC (Table of Contents) that stores bookmarks for the document. We use this data structure to build a structured file, then populate the content for each leaf node in the resulting tree.

## How to use
Type following into your command line
```
python main.py file_path
```

## Example structure
* Safety information:
    * page: 4
    * children:
        * About this guide:
            * page: 5
            * content: "..."
        * Package contents:
            * page: 6
            * content: "..."
        * TUF GAMING B650M-PLUS specifications summary:
            * page: 6
            * content: "..."
* Chapter 1 Product Introduction:
* Chapter 2 BIOS and RAID Support:
* Appendix: