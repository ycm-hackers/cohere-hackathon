from flask import Flask, request
import edgar_crawler
import cohere_embeddings
import weaviate_handler

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        ticker = request.form['ticker']
        text_chunks = edgar_crawler.crawl_for_ticker(ticker)
        embeddings = cohere_embeddings.generate_embeddings(text_chunks)
        
        weaviate_client = weaviate_handler.initialize_weaviate()
        weaviate_handler.index_data(weaviate_client, text_chunks, embeddings)

        return "Data indexed successfully for ticker: " + ticker
    return '''
              <form method="post">
                  Ticker Symbol: <input type="text" name="ticker"><br>
                  <input type="submit" value="Crawl and Index">
              </form>
           '''

if __name__ == '__main__':
    app.run(debug=True)
