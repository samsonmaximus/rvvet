# Reference check: methods.bib

Checked 2026-09-29. methods.bib has 90 entries and was not edited.

**Result: 90 OK, 0 FIX, 0 UNVERIFIED.**

## Method

- **Full check (4 new entries):** Aigrain2012, Pedregosa2011, Dumusque2017 and Zhao2022. For each, I checked the authors (the first author and every listed name, in order), year, title, journal, volume, pages and DOI against the Crossref record, or the JMLR page for Pedregosa2011 (JMLR has no DOIs).
- **Lighter pass (86 entries):** every DOI was resolved through Crossref, OpenAlex or the publisher, and the title, first author and year were checked. Where the record gave them, volume, pages and author order were compared too. Entries without a DOI (Mayor2003, LoCurto2015) were checked against ADS and ESO.
- **Changes from the source files:** apart from the 4 new entries, every methods.bib entry is field-for-field identical to its rvpaper_subset.bib or bench.bib version. The only change is that journal names are abbreviated (for example "Astronomy \& Astrophysics" became "A\&A"), and those abbreviations are correct.
- **Status rule:** FIX means a factual error in authors, year, title words, journal, volume, pages or DOI. Differences in hyphenation or spacing only are marked OK with a note. For them I give an optional correction.
- **Years:** OpenAlex and Crossref sometimes give the online-first year (for example 2008 for A&A vol. 493). The bib follows the volume or print year, which matches ADS and journal practice. **Do not "correct" these.**
- **Rate limits:** Crossref and OpenAlex returned HTTP 429 for a few URLs (Crossref for Bonfils2005, Mayor2009b and Jenkins2013; OpenAlex for SuarezMascareno2025, Marcy1998 and Rivera2010). I checked each of these through another source, shown in the table, so nothing is left unverified.

## Table

| key | status | problem | correction | source URL |
|---|---|---|---|---|
| Bonfils2005 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361:200500193 ; https://ui.adsabs.harvard.edu/abs/2005A&A...443L..15B |
| Udry2007 | OK | — | — | https://api.crossref.org/works/10.1051/0004-6361:20077612 |
| Mayor2009a | OK | — | — | https://api.crossref.org/works/10.1051/0004-6361/200912172 |
| Mayor2009b | OK | OpenAlex gives 2008 (online date); vol. 493 is Jan 2009, ADS 2009. Keep 2009. | — | https://api.openalex.org/works/doi:10.1051/0004-6361:200810451 ; https://ui.adsabs.harvard.edu/abs/2009A&A...493..639M |
| Vogt2010 | OK | — | — | https://api.crossref.org/works/10.1088/0004-637X/723/1/954 |
| Robertson2014 | OK | — | — | https://api.crossref.org/works/10.1126/science.1253253 |
| vonStauffenberg2024 | OK | All 21 authors match in order. | — | https://api.crossref.org/works/10.1051/0004-6361/202449375 |
| AngladaEscude2014 | OK | All 24 authors match in order. | — | https://api.crossref.org/works/10.1093/mnrasl/slu076 |
| Robertson2015 | OK | — | — | https://api.crossref.org/works/10.1088/2041-8205/805/2/L22 |
| Bortle2021 | OK | — | — | https://api.crossref.org/works/10.3847/1538-3881/abec89 |
| Jenkins2013 | OK | — | — | https://api.openalex.org/works/doi:10.1088/0004-637X/771/1/41 |
| Santos2014 | OK | All 24 authors match in order. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201423808 ; https://ui.adsabs.harvard.edu/abs/2014A&A...566A..35S |
| Faria2020 | OK | All 16 authors match in order. | — | https://api.crossref.org/works/10.1051/0004-6361/201936389 |
| Ma2018 | OK | — | — | https://api.openalex.org/works/doi:10.1093/mnras/sty1933 |
| Laliotis2023 | OK | All 25 authors match in order. | — | https://api.openalex.org/works/doi:10.3847/1538-3881/acc067 |
| Burrows2024 | OK | All 20 authors match in order. | — | https://api.openalex.org/works/doi:10.3847/1538-3881/ad34d5 |
| Ribas2018 | OK | — | — | https://api.openalex.org/works/doi:10.1038/s41586-018-0677-y |
| Lubin2021 | OK | All 20 authors match in order. | — | https://api.openalex.org/works/doi:10.3847/1538-3881/ac0057 |
| GonzalezHernandez2024 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202451311 |
| Basant2025 | OK | — | — | https://api.openalex.org/works/doi:10.3847/2041-8213/adb8d5 |
| Wittenmyer2014 | OK | — | — | https://api.openalex.org/works/doi:10.1088/0004-637X/791/2/114 |
| Gorrini2022 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202243063 ; https://ui.adsabs.harvard.edu/abs/2022A&A...664A..64G |
| Tuomi2018 | OK | — | — | https://api.openalex.org/works/doi:10.3847/1538-3881/aab09c |
| Carleo2020 | OK | Cosmetic only: publisher title spells it "case study"; the bib has "case-study". Not a factual error. | Optional: title `... A {GIARPS} case study of known young ...` | https://www.aanda.org/articles/aa/full_html/2020/06/aa37369-19/aa37369-19.html |
| Dumusque2012 | OK | — | — | https://api.openalex.org/works/doi:10.1038/nature11572 |
| Rajpaul2016 | OK | OpenAlex gives 2015 (online date); vol. 456 is 2016, ADS 2016. Keep 2016. | — | https://api.openalex.org/works/doi:10.1093/mnrasl/slv164 |
| Endl2008 | OK | — | — | https://api.openalex.org/works/doi:10.1086/524703 |
| Forveille2009 | OK | OpenAlex gives 2008 (online date); vol. 493 is Jan 2009. Keep 2009. | — | https://api.openalex.org/works/doi:10.1051/0004-6361:200810557 ; https://ui.adsabs.harvard.edu/abs/2009A&A...493..645F |
| AngladaEscude2013 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201321331 |
| RobertsonMahadevan2014 | OK | — | — | https://api.openalex.org/works/doi:10.1088/2041-8205/793/2/L24 |
| FerozHobson2014 | OK | OpenAlex gives 2013 (online date); vol. 437 is 2014. Keep 2014. | — | https://api.openalex.org/works/doi:10.1093/mnras/stt2148 |
| Pepe2011 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201117055 |
| Nari2025 | OK | OpenAlex gives 2024 (online date); vol. 693 is Jan 2025, ADS 2025. Keep 2025. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202451769 ; https://ui.adsabs.harvard.edu/abs/2025A%26A...693A.297N |
| Tuomi2013a | OK | All 15 authors match in order. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201220509 ; https://ui.adsabs.harvard.edu/abs/2013A&A...551A..79T |
| Feng2017 | OK | — | — | https://api.openalex.org/works/doi:10.3847/1538-3881/aa83b4 |
| Tuomi2013b | OK | OpenAlex gives 2012 (online date); vol. 549 is Jan 2013. Keep 2013. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201220268 |
| Diaz2016 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201526729 ; https://ui.adsabs.harvard.edu/abs/2016A&A...585A.134D |
| Udry2019 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201731173 ; https://ui.adsabs.harvard.edu/abs/2019A&A...622A..37U |
| Kane2020 | OK | — | — | https://api.openalex.org/works/doi:10.3847/1538-3881/aba835 |
| Delrez2021 | OK | — | — | https://www.nature.com/articles/s41550-021-01381-5 |
| Huang2018 | OK | — | — | https://api.openalex.org/works/doi:10.3847/2041-8213/aaef91 |
| Gandolfi2018 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201834289 ; https://ui.adsabs.harvard.edu/abs/2018A&A...619L..10G |
| Luque2019 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201935801 |
| BertaThompson2015 | OK | — | — | https://api.openalex.org/works/doi:10.1038/nature15762 |
| Gandolfi2019 | OK | Cosmetic only: published title writes "HD15337" (no space); the bib has "HD 15337". | Optional: `{HD}15337` | https://iopscience.iop.org/article/10.3847/2041-8213/ab17d9 |
| Dumusque2019 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201935457 |
| AngladaEscude2016 | OK | — | — | https://api.openalex.org/works/doi:10.1038/nature19106 |
| SuarezMascareno2020 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202037745 ; https://ui.adsabs.harvard.edu/abs/2020A&A...639A..77S |
| Faria2022 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202142337 |
| SuarezMascareno2025 | OK | — | — | https://api.crossref.org/works/10.1051/0004-6361/202553728 ; https://ui.adsabs.harvard.edu/abs/2025A&A...700A..11S |
| Rosenthal2021 | OK | — | — | https://api.openalex.org/works/doi:10.3847/1538-4365/abe23c |
| Butler2004 | OK | — | — | https://api.openalex.org/works/doi:10.1086/425173 |
| Gillon2007 | OK | — | — | https://api.openalex.org/works/doi:10.1051/0004-6361:20077799 |
| Marcy1998 | OK | — | — | https://iopscience.iop.org/article/10.1086/311623 ; https://ui.adsabs.harvard.edu/abs/1998ApJ...505L.147M |
| Rivera2010 | OK | — | — | https://iopscience.iop.org/article/10.1088/0004-637X/708/2/1492 |
| Howard2011 | OK | All 10 authors match in order. | — | https://api.openalex.org/works/doi:10.1088/0004-637X/730/1/10 |
| Trifonov2018 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2018A&A...609A.117T |
| Lovis2011 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2011A&A...528A.112L |
| Bouchy2009 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2009A&A...496..527B |
| Horner2019 | OK | All 10 authors match in order. | — | https://api.openalex.org/works/doi:10.3847/1538-3881/ab2e78 |
| Bonfils2013 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2013A&A...556A.110B |
| Trifonov2020 | OK | All 6 authors match in order. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201936686 ; https://ui.adsabs.harvard.edu/abs/2020A&A...636A..74T |
| Zechmeister2018 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2018A&A...609A..12Z |
| ZechmeisterKurster2009 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2009A&A...496..577Z |
| Sreenivas2022 | OK | All 6 authors match. Cosmetic only: the A&A HTML title writes "HD103891 and HD105779" (no spaces); arXiv/ADS use spaces as in the bib. | — | https://www.aanda.org/articles/aa/abs/2022/04/aa42612-21/aa42612-21.html |
| LilloBox2021 | OK | arXiv eprint 2109.00226 also confirmed. | — | https://ui.adsabs.harvard.edu/abs/2021A&A...654A..60L |
| Mayor2003 | OK | No DOI (The Messenger). | — | https://ui.adsabs.harvard.edu/abs/2003Msngr.114...20M |
| LoCurto2015 | OK | No DOI (The Messenger). | — | https://ui.adsabs.harvard.edu/abs/2015Msngr.162....9L |
| ChenKipping2017 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2017ApJ...834...17C |
| Kipping2013 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2013MNRAS.434L..51K |
| Noyes1984 | OK | — | — | https://ui.adsabs.harvard.edu/abs/1984ApJ...279..763N |
| Mamajek2008 | OK | — | — | https://api.openalex.org/works/doi:10.1086/591785 |
| Boisse2011 | OK | All 6 authors match in order. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/201014354 ; https://ui.adsabs.harvard.edu/abs/2011A&A...528A...4B |
| Nava2020 | OK | All 4 authors match. OpenAlex gives 2019 (online date); vol. 159 is 2020, ADS 2020AJ....159...23N. Keep 2020. | — | https://api.openalex.org/works/doi:10.3847/1538-3881/ab53ec |
| Rajpaul2015 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2015MNRAS.452.2269R |
| Harris2020 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2020Natur.585..357H |
| Virtanen2020 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2020NatMe..17..261V |
| Hunter2007 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2007CSE.....9...90H |
| Perdelwitz2024 | OK | All 5 authors match in order. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202348263 |
| Baluev2008 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2008MNRAS.385.1279B |
| Diaz2018 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2018AJ....155..126D |
| Hara2022 | OK | All 5 authors match. OpenAlex gives 2021 (online date); vol. 663 is 2022, ADS 2022. Keep 2022. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202140543 ; https://ui.adsabs.harvard.edu/abs/2022A&A...663A..14H |
| MortierCC2017 | OK | — | — | https://ui.adsabs.harvard.edu/abs/2017A&A...601A.110M |
| Hara2022b | OK | All 4 authors match. OpenAlex gives 2021 (online date); vol. 658 is Feb 2022. Keep 2022. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202141197 |
| GomesdaSilva2021 | OK | OpenAlex gives 2020 (online date); vol. 646 is 2021, ADS 2021. Keep 2021. | — | https://api.openalex.org/works/doi:10.1051/0004-6361/202039765 ; https://ui.adsabs.harvard.edu/abs/2021A&A...646A..77G |
| Yu2024 | OK | arXiv eprint 2401.05528 also confirmed. | — | https://api.openalex.org/works/doi:10.1093/mnras/stae137 ; https://ui.adsabs.harvard.edu/abs/2024MNRAS.528.5511Y |
| Aigrain2012 | OK | FULL CHECK: all 3 authors (Aigrain, Pont, Zucker), 2012, title, MNRAS 419, 3147-3158, DOI all match. Optional: issue 4 is missing (not an error). | — | https://api.crossref.org/works/10.1111/j.1365-2966.2011.19960.x |
| Pedregosa2011 | OK | FULL CHECK: the 6 listed authors (Pedregosa, Varoquaux, Gramfort, Michel, Thirion, Grisel) plus 'others' (16 in total), 2011, title, JMLR 12, 2825-2830 all match. JMLR gives no DOI, so none is expected. | — | https://jmlr.org/papers/v12/pedregosa11a.html |
| Dumusque2017 | OK | FULL CHECK: the 6 listed authors (Dumusque, Borsa, Damasso, Díaz, Gregory, Hara) plus 'others' (25 in total), 2017, title, A&A 598, A133, DOI all match. | — | https://api.crossref.org/works/10.1051/0004-6361/201628671 |
| Zhao2022 | OK | FULL CHECK: the 5 listed authors (Zhao L. L., Fischer, Ford, Wise, Cretignier) plus 'others' (43 in total), 2022, title, AJ 163, 171, DOI all match. Optional: issue 4 is missing (not an error). | — | https://api.crossref.org/works/10.3847/1538-3881/ac5176 |

## Corrected BibTeX for FIX entries

None. No entry has a factual error, so no replacement BibTeX is needed.

Optional cosmetic changes to match publisher title typography exactly (not required):

```bibtex
% Carleo2020: publisher title uses "case study" (no hyphen)
  title   = {The {GAPS} Programme at {TNG}. {XXI}. A {GIARPS} case study of known young planetary candidates: confirmation of {HD} 285507 b and refutation of {AD Leonis} b},

% Gandolfi2019: published title writes HD15337 without a space
  title   = {The Transiting Multi-planet System {HD}15337: Two Nearly Equal-mass Planets Straddling the Radius Gap},
```
