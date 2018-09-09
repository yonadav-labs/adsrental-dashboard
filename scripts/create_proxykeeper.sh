#!/usr/bin/env bash

apt install ssh

useradd proxykeeper -m -p keepitsecret

su - proxykeeper

mkdir -p ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD2/FUH0n58G7Y7yLzrYHKfcqACuBcL37e8ft+SllLEJzsDTqAFoUja0xDzWSBpuqn5R7DOfayWsgId2HO9osoW4YwkvmG7KD84dDpUPtV6fNZPpc6qlXd3FcbVE94mdrYUYrGF8hZYZ0hh3Gmc04j0qaPq5e5Z7/mO1aZpY+Kkumseuzu1dkx/Bk0Tm5BakWb7q147bWKdFmbnnHPq8hH2YLcIjOfKs+gaK0yP4W96xASHEp0O3PJjZY40ik6ZFDaEd6NL1RS0wAknqtjwF8OLKG9348t2Uyqhp6X4rDAMt3bfR8Ix4NVYHbLA2Wa/5L0JszXHWfWRpr291SJvf9LX vlad@vlad-XPS-15-9560" >> ~/.ssh/autorized_keys

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABADoDa7+1N6TKE2Xw7M7i59Pz6XBvM9JunoA7VnTxbxxC5icd/KxLhn8tZZLJ2d4ly0Lx3zzhttfuoo2G/XDIEEQ+doEE56F3Qgso/SS/U2Xj/oqgk50ZNPnGhrZ9h9zVok5h0fy3nH7wzyQCoiiVL74PywniqVsbG8OxcfXANTu8+j8sM5azsX895rfBBdNfoJnmlB5LNgpeCjO6Sr6PzE2XjOe6XCG53hv3VTJNlSgPvr0XAtKyd76dfkaAF0FI3j1tcLgTjJ1w/uZ1oSieUjaNNKz3wHSD3aXt3SRVHu6/MJHbz0GP7DESZ+LRmdbQjibHJOahTotLNfndUp7UuXc= Administrator@EC2" >> ~/.ssh/id_rsa.pub

echo "-----BEGIN RSA PRIVATE KEY-----" > ~/.ssh/id_rsa
echo "MIIEnwIBAAKCAQA6A2u/tTekyhNl8OzO4ufT8+lwbzPSbp6AO1Z08W8cQuYnHfys" >> ~/.ssh/id_rsa
echo "S4Z/LWWSydneJctC8d884bbX7qKNhv1wyBBEPnaBBOehd0ILKP0kv1Nl4/6KoJOd" >> ~/.ssh/id_rsa
echo "GTT5xoa2fYfc1aJOYdH8t5x+8M8kAqIolS++D8sJ4qlbGxvDsXH1wDU7vPo/LDOW" >> ~/.ssh/id_rsa
echo "s7F/Pea3wQXTX6CZ5pQeSzYKXgozukq+j8xNl4znulwhud4b91UyTZUoD769FwLS" >> ~/.ssh/id_rsa
echo "sne+nX5GgBdBSN49bXC4E4ydcP7mdaEonlI2jTSs98B0g92l7d0kVR7uvzCR289B" >> ~/.ssh/id_rsa
echo "j+wxEmfi0ZnW0I4mxyTmoU6LSzX53VKe1Ll3AgMBAAECggEAHpaNKnCnXSj7H2Xv" >> ~/.ssh/id_rsa
echo "xonXSGcz74eCoHKY+e3PgSuHtTQE3B0wi7vqt4W9J69sQ3hT+wFC/nvYh3QYm1zQ" >> ~/.ssh/id_rsa
echo "prWl9gWlQBPQ+c7CsNW027pRg8i5/mf6TPvsdcJaZ0A68ZJm2MM1D/XT+w6HeWo2" >> ~/.ssh/id_rsa
echo "DAXVPXZgTN8JArOBaSZXewcUSmGyO2h2a31h2BzYwGTMHVdzmnkL9WFRxSNuxDmj" >> ~/.ssh/id_rsa
echo "68wjEbLiudXH9y3bRUbn8E2iVhtTaKByae8MTKko+RaEYkGWusWTG6KD3FStyiMC" >> ~/.ssh/id_rsa
echo "duxhel9svIlSuWuyYDQtBzKnvKh4gq7K4tXzHp9ARrOvDYi0iSF4Dq6TW7FJ48O5" >> ~/.ssh/id_rsa
echo "DlcGmQKBgH/g5QovqGfosh3CtQroBUDex4ws/XKP75xN5AidX0MN1lpli7ilbypc" >> ~/.ssh/id_rsa
echo "aiDPwH4imXzF3aGyziBA4k/eXKbxoOuw2QHQl+7cCTBKlbdLgv96Xo6P58XB/wnD" >> ~/.ssh/id_rsa
echo "g+GWKQStktPlnUjKv2KQSSyVWqyEwpjJnV7BT+lCw6TI3UOt/L67AoGAdCMQc43p" >> ~/.ssh/id_rsa
echo "Epdc/nlq3TuH4ngMJMQM+5RK+RdBgoGPBHfUbTNYRLG+zA3yYXEY3k3O6T/hUmiU" >> ~/.ssh/id_rsa
echo "ng04/MSk/L961ltxzKoVjahzIjy22AgwLNIAO+QbB+LmiD6dp7IuCWIWboD/quEq" >> ~/.ssh/id_rsa
echo "HwuixIAlcWeZpRJw9ApJgVwGHU69oLtWynUCgYBmRrjpLLTEZpgOtWuXDXsmJwfy" >> ~/.ssh/id_rsa
echo "VQlgVz6NBL8dJMDMIIUQR6c4RxhiCQfYtlB+ka2w3ZAlg5zYrwxSVMZFv3u1BfyK" >> ~/.ssh/id_rsa
echo "NwtNPy8aMI0NzJc5PeXin7X/tOkGJhmUk0S7ORf14e+qCH6JllzwC4Q59vSsvpPe" >> ~/.ssh/id_rsa
echo "9T20knFnmj9dogpDgQKBgFgwgD+fVYuekSlUPgf9OrSIgIAyt8Ea3MvGEyLtCxNT" >> ~/.ssh/id_rsa
echo "g2XhBXg0mTQOqy2/WikFYMfSkGGptKFIXSvkj3y2UqsQCZxm07McZUFsZVQq85o1" >> ~/.ssh/id_rsa
echo "ZaQVFUmpzXFMSx+auEa7y1jicELsdLXaeiFJRiWVjCDDni5S2Xp3zNTYhDrXx5I5" >> ~/.ssh/id_rsa
echo "AoGALk4SlHraD5o6llOPLmvUQAUeorZJlhjxt8z7ZJRUwQOzKmMfiV7suP53iNuv" >> ~/.ssh/id_rsa
echo "cxg4QdyrrtQ3FTwlPu4KDuZoM28GOW6WA3X+tBHcfN/bRVqtj4GJsaFGC0qMt3mt" >> ~/.ssh/id_rsa
echo "DgUp2pyYhjUzFrAm1akbXivBSn17HoJ2bKY35wa+qJxfEB4=" >> ~/.ssh/id_rsa
echo "-----END RSA PRIVATE KEY-----" >> ~/.ssh/id_rsa

chmod 400 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub