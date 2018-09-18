https://ugene.net/wiki/pages/viewpage.action?pageId=22544386

Что ожидается от скрипта:
Скрипт должен проверять наличие новых данных на внешних серверах (NCBI, uniprot) и, если там есть более свежие данные, то скачать их, обновить базы данных, разложить правильным образом, подготовить обновление репозитория для инсталлятора и закачать обновленные данные на сервер.

Скрипт должен быть максимально платформонезависимым. Предлагаю написать его на python 2.



Что может ожидать скрипт:
Скрипт может рассчитывать, что путь до repogen есть в переменной PATH, а также, что рядом с ним лежит содержимое репозитория ugene-installer и external tool'ы, которые были в последнем релизе.



Скрипт должен принимать следующие аргументы:
Пусть до репозитория инсталлятора (папка, содержащая файл Updates.xml)



Шаги:
* Скачать файл Updates.xml.
* Вытащить из него текущие версии нужных компонентов
* Сделать отдельную ветку в гите для проекта ugene-installer
* Для каждого компонента:
    * Проверить, есть ли на сервере более свежая версия
    * Если есть обновления, то скачать обновленные данные
    * Обработать данные надлежащим образом (разложить как надо, собрать базы etc)
    * Обновить метаинформацию (версия и дата)
    * Запустить утилиту repogen
    * Закачать на сервер данные компонентов
* Сделать резервную копию файла Updates.xml на сервере
* Закачать на сервер новый Updates.xml
* Влить ветку в гите в master


Компоненты:<br/>
**ngs_classification.diamond.uniref50_database**

Версия вида "2018_07".

Версию можно вытащить отсюда: ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/RELEASE.metalink

Обработка:

скачать ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz
скачать (или найти локально на компе, если таксономия не обновлялась) таксономические данные: taxonomy/prot.accession2taxid.gz, taxonomy/nodes.dmp
запустить diamond с аргументами

./diamond --in uniref50.fasta.gz --db uniref50.dmnd --taxonmap taxonomy/prot.accession2taxid.gz --taxonnodes taxonomy/nodes.dmp}


На выходе будет один файл. Его надо положить в папку "ngs_classification.diamond.uniref50_database/data/data/ngs_classification/diamond/uniref".




**ngs_classification.diamond.uniref90_database**

Версия вида "2018_07".

Версию можно вытащить отсюда: ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref90/RELEASE.metalink

Обработка:

скачать ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref90/uniref90.fasta.gz
скачать (или найти локально на компе, если таксономия не обновлялась) таксономические данные: taxonomy/prot.accession2taxid.gz, taxonomy/nodes.dmp
запустить diamond с аргументами

diamond --in uniref90.fasta.gz --db uniref90.dmnd --taxonmap taxonomy/prot.accession2taxid.gz --taxonnodes taxonomy/nodes.dmp


На выходе будет один файл. Его надо положить в папку "ngs_classification.diamond.uniref90_database/data/data/ngs_classification/diamond/uniref"


**ngs_classification.kraken.minikraken_4gb_database**

Версия вида "20171019"

Версию надо вытащить из имени файла. Проблема в том, что для того, чтобы найти файл, надо знать версию. Но можно попробовать распарсить страницу https://ccb.jhu.edu/software/kraken/, там есть ссылка на последнюю версию.
Обработка:

скачать https://ccb.jhu.edu/software/kraken/dl/minikraken_20171019_4GB.tgz - дата может быть другая.
содержимое архива надо положить в папку "ngs_classification.kraken.minikraken_4gb_database/data/data/ngs_classification/kraken/minikraken_4gb"

**ngs_classification.taxonomy**

Версии как таковой нет. В качестве версии надо использовать дату в формате "ГГГГММДД"

Обработка:

скачать пять файлов отсюда: ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/*. 
<br/>Файлы: 
* nucl_est.accession2taxid.gz
* nucl_gb.accession2taxid.gz
* nucl_gss.accession2taxid.gz
* nucl_wgs.accession2taxid.gz
* prot.accession2taxid.gz

распаковать четыре из пяти фалов: nucl*
<br/>скачать **ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz**<br/>
распаковать **taxdump.tar.gz**
удалить все, кроме следующих файлов: 
* merged.dmp
* names.dmp
* nodes.dmp
* nucl_est.accession2taxid
* nucl_gb.accession2taxid
* nucl_gss.accession2taxid
* nucl_wgs.accession2taxid
* prot.accession2taxid.gz

сложить оставшиеся файлы в папку "ngs_classification.taxonomy/data/data/ngs_classification/taxonomy"

**ngs_classification.refseq.grch38**
Версию можно взять здесь: ftp://ftp.ncbi.nih.gov/refseq/RELEASE_NUMBER

Обработка:

скачать файлы ftp://ftp.ncbi.nih.gov/refseq/H_sapiens/H_sapiens/CHR_*/hs_ref_GRCh38.p12_chr*.fa.gz (всего 24 файла)
сложить эти архивы в папку "ngs_classification.refseq.grch38/data/data/ngs_classification/refseq/human"

**ngs_classification.refseq.viral**
Версию можно взять здесь: ftp://ftp.ncbi.nih.gov/refseq/RELEASE_NUMBER

Обработка:

скачать файлы ftp://ftp.ncbi.nlm.nih.gov/refseq/release/viral/*.genomic.fna.gz
сложить эти архивы в папку "ngs_classification.refseq.viral/data/data/ngs_classification/refseq/viral"

**ngs_classification.refseq.bacterial**
Версию можно взять здесь: ftp://ftp.ncbi.nih.gov/refseq/RELEASE_NUMBER

Обработка:

скачать файлы ftp://ftp.ncbi.nlm.nih.gov/refseq/release/bacteria/*.genomic.fna.gz
сложить эти архивы в папку "ngs_classification.refseq.bacterial/data/data/ngs_classification/refseq/bacterial"

**ngs_classification.clark.bacterial_viral_database**

Версия такая же как у компонентов ngs_classification.refseq.bacterial и ngs_classification.refseq.viral.
Этот компонент надо обновлять, если были изменены компоненты ngs_classification.refseq.bacterial или ngs_classification.refseq.viral

Обработка:

создать базу из данных (надо подсмотреть в коде UGENE алгоритм)

**ngs_classification.clark.viral_database**

Версия такая же как у компонента ngs_classification.refseq.viral.

Этот компонент надо обновлять, если был изменен компонент ngs_classification.refseq.viral

Обработка:

создать базу из данных (надо подсмотреть в коде UGENE алгоритм)


Замечания:
Если дата не записана в каком-нибудь файле рядом с данными, то надо брать дату последней модификации (создания?) файла. Если файлов больше, чем один, то можно взять самый древний, или действовать по усмотрению.

Версия должна быть строго больше, чем то, что есть у нас.