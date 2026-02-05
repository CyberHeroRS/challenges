# web_2 solution

1. Register as user `a\n../../../../frontend/` - this bypasses username filter, because there is a regex arror - m option is there, which is multiline, so the `^` and `$` match start and end of line, not start and end of string. This way, we can bypass the filter.
2. Upload a `.html` file with this content: `<br inline-source src="../../flag.txt" />` - This uses vite-plugin-inline-source, which has no checks for file type or tag type (meaning <br> could be anything else) -> so it just reads the flag and puts it in the HTML when processed with vite.
3. That's uploaded to the frontend, but it's saved using the timestamp - we use the `Date` header from the `/upload` response to get the timestamp of when the file was made (so now we know the uploaded file's name).
4. Visit `/_{timestamp}.html` to get it to "execute" and print the flag.
5. Profit.