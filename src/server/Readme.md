server  
python httpfs.py -v -d /server/data -p 8007

get  
python httpc.py get -v -url 'http://localhost:8007/test.txt'
python httpc.py post -h Content-Type:application/json -f test.txt -url http://httpbin.org/post
python httpc.py post -h Content-Type:application/json -f sample.txt -url http://localhost:8007/post
python httpc.py get -url  'http://localhost:8007/sample-folder/test.txt'

post  
python httpc.py post -h Content-Type:application/json -d '{"Assignment": 77}' -url http://localhost:8088/sample-folder/test.py  
python httpc.py post -h Content-Type:application/json -d '{"Assignment": 3}' -url http://localhost:80/test.py
python httpc.py post -h Content-Type:application/json -d '{"Assignment": 2}' -url http://localhost:80/test.txt
403  
python httpc.py get -url 'http://localhost:80/../c:/test.txt'  
  
404  
python httpc.py get -url 'http://localhost:80/c:/test.txt'  