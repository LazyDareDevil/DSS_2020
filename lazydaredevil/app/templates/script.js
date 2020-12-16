var net = require('net');

var client = new net.Socket();
client.connect(8484, '127.0.0.1', function() {
    console.log('Connected');
});

client.on('data', function(data) {
    console.log('Received: ' + data);
	if (data == "err"){
		document.getElementById("m").innerHTML = "Something went wrong, try to rebuild app";
		client.destroy();
	}
    if (data == "waita"){
		document.getElementById("m").innerHTML = "Waiting for analyze to be done";
	}
	if (data == "done"){
		document.getElementById("m").innerHTML = "";
		document.getElementById("done").appendChild(document.createElement('h2').innerHTML("Sentiment trend in time"));
		var image = document.createElement('img')
		image.src  = 'test_sentiment.png'
		document.getElementById("done").appendChild(image)
		document.getElementById("done").appendChild(document.createElement('h2').innerHTML("Key words"));
		var image = document.createElement('img')
		image.src  = 'test_keywords.png'
		document.getElementById("done").appendChild(image)
		client.destroy();
	}
});

// <def id="done"><h2>Sentiment trend in time</h2><img src="test_sentiment.png" width="2000" height="530"><h2>Keyword trend</h2><img src="test_keywords.png" width="600" height="600"></def>