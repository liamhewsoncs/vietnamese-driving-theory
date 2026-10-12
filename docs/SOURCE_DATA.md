# Official source data

The source PDF is intentionally not redistributed in this repository or its ZIP release. To rebuild the data, download the [official CSGT 600-question bank](https://www.csgt.vn/upload/services/273963059_B%E1%BB%99%20600%20c%C3%A2u%20h%E1%BB%8Fi%20d%C3%B9ng%20cho%20s%C3%A1t%20h%E1%BA%A1ch%20l%C3%A1i%20xe%20c%C6%A1%20gi%E1%BB%9Bi%20%C4%91%C6%B0%E1%BB%9Dng%20b%E1%BB%99.pdf). The publisher also provides [guidance on use of the question bank](https://lab.csgt.vn/upload/services/2071319603_H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20s%E1%BB%AD%20d%E1%BB%A5ng%20b%E1%BB%99%20c%C3%A2u%20h%E1%BB%8Fi%20s%C3%A1t%20h%E1%BA%A1ch%20GPLX%20%28CV%202262.07.5.2025%29.pdf).

Save the downloaded bank as `source/official-600-questions.pdf` in this project. That path is ignored by Git. Run `python extract_questions.py` from the project folder, followed by the validation commands in the README.

If the publisher updates its documents, compare the new edition against the bundled questions and answers before replacing the data. English text, especially machine-translated text, should be checked against the current Vietnamese source by a qualified reviewer.
