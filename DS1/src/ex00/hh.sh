#/bin/sh


VACANCY="20"


curl -s "https://api.hh.ru/vacancies?text=$1&page=0&per_page=$VACANCY" | jq > hh.json
