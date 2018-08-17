python3 setup.py install
git clone https://github.com/InnovativeInventor/monobox-example
cp tests/goss.yaml monobox-example/goss.yaml
cd monobox-example
goss validate || ((i++))
echo "$i"
exit $i