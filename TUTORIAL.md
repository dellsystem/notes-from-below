# How to use the admin interface

Message me if you have questions.

## Uploading files

Any kind of file can be uploaded. There are special features for images (which are displayed) and PDFs (which are embedded); other files are simply linked to.

From the main admin page, click on "Image uploads" or "Pdf uploads" or "Other uploads" (under UPLOADS) and to upload a file. Set the title to something descriptive—the slug field will automatically be populated from there. You can think of the slug as the (unique) name which you'll use to refer to this file in order to embed it within an article.

For example, if you upload an image with the slug `test-image-1`, you can embed it within an article using the following code:

```
[img:test-image-1]
```

If you want to add a caption below it:

```
[img:test-image-1 This is a caption]
```

If you have multiple images that you want to appear on the same line and don't need a caption, use:

```
[images:test-image-1 test-image-2 test-image-3]
```

Embedding a PDF is similar. Upload it under "Pdf uploads" and make a note of the slug (e.g., `test-bulletin-1`). Then embed it like this:

```
[pdf:test-bulletin-1]
```

To add a link to any other type of file (e.g. a docx, or an epub), upload it under "Other uploads" with the slug `test-epub`, title `Some File To Download`, and extension `epub`, and embed it like this:

```
[file:test-epub]
```

When the article is published, it will be converted into a large red button that says "Download Some File To Download (epub)", with a link to the file.

## Previewing articles

To preview an article before it's published, make sure the "Published" field (under the image) is unchecked, and click the "View on site" button (top right) on the article edit page after the article has been created.

## Adding translations

From the main admin page, click on "Article translations" (under JOURNAL) and add a new one. Select the relevant article and the language (we currently only support Spanish and Polish). You can only add one translation for each article-language combination.

The link for the translated article is just the article link plus ?language=es (or whatever the language code is) at the end.

## Changing the order of articles on the homepage

Currently, all published articles are shown on the homepage, ordered according to the "Order in issue" field which you can change in the article edit page in the admin. Set the order to 0 to display a larger article image (stretched across two columns) at the top.
