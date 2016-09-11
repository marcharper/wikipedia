
mediawiki_namespaces = [
    "Media", "Special","Talk", "User", "User Talk", "Wikipedia", "Wikipedia talk",
    "Image", "Image_talk", "MediaWiki", "MediaWiki talk", "Template",
    "Template talk", "Help", "Help talk", "Category", "Category talk", "Project",
    "Project talk", "Portal", "Portal talk", "wp", "wt", "Wiktionary",
    "Wikibooks", "Wikisource", "Wikiquote", "Meta"]

mediawiki_namespaces = map(lambda x: x.lower(), mediawiki_namespaces)

mediawiki_interwiki_prefix = [
    'wikipedia', 'w', 'wikitionary', 'wikt', 'wikinews', 'n', 'wikibooks', 'b',
    'wikiquote','q', 'wikisource', 's', 'wikispecies', 'wikiversity', 'v',
    'wikimedia', 'wmf', 'commons', 'meta', 'm', 'incubator', 'mediawiki', 'mw',
    'mediazilla', 'testwiki']

mediawiki_language_codes = [
    'aa', 'ab', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'as', 'ast',
    'av', 'ay', 'az', 'ba', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg',
    'bh', 'bi', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca',
    'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'closed-zh-tw',
    'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'da', 'de', 'diq', 'dsb',
    'dv', 'dz', 'ee', 'el', 'eml', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'ff',
    'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'fur', 'fy', 'ga', 'gd', 'gl',
    'glk', 'gn', 'got', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'ho', 'hr',
    'hsb', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo',
    'io', 'is', 'it', 'iu', 'ja', 'jbo', 'jv', 'ka', 'kab', 'kg', 'ki', 'kj',
    'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky',
    'la', 'lad', 'lb', 'lbe', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lt', 'lv',
    'map-bms', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'mus',
    'my', 'mzn', 'na', 'nah', 'nan', 'nap', 'nds', 'nds-nl', 'ne', 'new', 'ng',
    'nl', 'nn', 'no', 'nov', 'nrm', 'nv', 'ny', 'oc', 'om', 'or', 'os', 'pa',
    'pag', 'pam', 'pap', 'pdc', 'pi', 'pih', 'pl', 'pms', 'ps', 'pt', 'qu', 'rm',
    'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rw', 'sa', 'sc', 'scn',
    'sco', 'sd', 'se', 'sg', 'sh', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so',
    'sq', 'sr', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'ta', 'te', 'tet', 'tg',
    'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tokipona', 'tpi', 'tr', 'ts', 'tt',
    'tum', 'tw', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vi', 'vls',
    'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'yi', 'yo', 'za', 'zea', 'zh',
    'zh-classical', 'zh-min-nan', 'zh-yue', 'zu']

disambiguation_templates = [
    'disambig', 'disambig-cleanup', 'hndis', 'hndis-cleanup', 'geodis',
    'mountainindex', 'hospitaldis', 'powdis', 'schooldis', 'roaddis',
    'airport disambig', 'shipindex','mathdab','numberdis']
