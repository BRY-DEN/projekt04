from collector import run_collector

offers = run_collector()

print(offers[0])
print(*[offer.full_description() for offer in offers[:4]], sep="\n")
