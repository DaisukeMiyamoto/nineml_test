import nineml

items = nineml.read("xml/neurons/HodgkinHuxley.xml")
#items = nineml.read("xml/neurons/LeakyIntegrateAndFire.xml")
print items

model = items['HodgkinHuxley']

#items['LeakyIntegrateAndFire']
