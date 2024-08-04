Completed:

- refactored codebase and data:
  - clean organization of code with full postgres support
  - clean data and schema organization based on data source
- automatic siiir detection based using Levenstein distance

To do next:

1. Unfork PG schema: current scripts upload to bacplus (not public) schema.
   - Add necessary columns to public tables (bac, en)
   - Make new scripts compute old columns (id_liceu, id_judet, etc.)
   - Run new scripts on old schema
2. Improve SIIIR codes
   - Create script to update institution table with missing SIIIR codes from previous years (except current year where codes are guessed)
   - Change siiir detection to use institutions table instead of SIIIR
   - Change text fields "da"/"nu" to boolean in institutii table and update web app accordingly
   - Change webapp so that SIIIR codes are used as IDs instead of name based ids. Will require moving logos around on the file storage
   - Remove institutions without SIIIR code from institutii
3. Improve build time / ISR
   - Make it so that institution pages are generated statically on demand (not at build time)
   - Make it so that ranking pages are also generated statically. It will be tricky with static data (to be fetched from client), but it is necessary for ISR on logo updates. It will also speed up build time
   - Make logo updates trigger ISR
4. Admin dashboard
   - Create a page to edit individual school information (sigla, adresa, website, social links, program)
   - Create a page to search schools and open their edit page
   - Add istoric with nice editor that compiles to markdown (allowing bold, italic, bullets, etc)
   - Add file upload for orar, program, other documents. Show them on the public school page
   - Add image upload. Show them on the public school page.
5. Notify schools to update their pages
