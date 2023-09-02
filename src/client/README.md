# Comp445A1

Militsa Bogdeva - 40133261  
Graeme Killick - 40089907 

for help: python httpc.py help  

python httpc.py get example  
python httpc.py get -url 'http://httpbin.org/get?course=networking&assignment=1'  
python httpc.py get -v -url 'http://httpbin.org/get?course=networking&assignment=1'  
python httpc.py get -v -url 'http://httpbin.org/get?course=networking&assignment=1' -o hello.txt  

python httpc.py post example  
python httpc.py post -h Content-Type:application/json -d '{"Assignment": 1}' -url http://httpbin.org/post  
python httpc.py post -h Content-Type:application/json -f test.txt -url http://httpbin.org/post  

python redirect example   
python httpc.py get -v -url http://httpbin.org/absolute-redirect/5  
python httpc.py get -v -url http://httpbin.org/relative-redirect/5  


should not work because -d and -f are present  
python httpc.py post -v -h test:this -h again:this -f test.txt -d "whatever" urltoload

should not work because it is a get request and -d or -f are present  
python httpc.py get -v -h test:this -h again:this -d "whatever" -url urltoload  
python httpc.py get -v -h test:this -h again:this -f test.txt -url urltoload  

for multiple headers  
python httpc.py get -v -h test:this -h again:this -url http://httpbin.org/sdfs  