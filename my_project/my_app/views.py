import requests
import datetime
from django.conf import settings
from django.shortcuts import render
from notion_client import Client
from .models import Book
from jpndlpy import JapanNdlClient
from django.http import JsonResponse

notion = Client(auth=settings.NOTION_API_KEY)

def get_book_info(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    data = response.json()

    if data["totalItems"] == 0:
        return None

    volume_info = data["items"][0]["volumeInfo"]
    title = volume_info.get("title", "Unknown")
    authors = volume_info.get("authors", ["Unknown"])
    author = authors[0]
    cover_image_url = volume_info.get("imageLinks", {}).get("thumbnail", "")

    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "cover_image_url": cover_image_url,
    }


def add_book_to_notion(database_id, book):
    # Notionページを作成
    new_page = {
        "Title": {"title": [{"text": {"content": book.title}}]},
        "Author": {"rich_text": [{"text": {"content": book.author}}]},
        "ISBN": {"rich_text": [{"text": {"content": book.isbn}}]},
        "Registration Date": {"date": {"start": datetime.datetime.now().isoformat()}},
        "Cover Image": {"url": book.cover_image_url}
    }

    # データベースに新しいページを追加
    notion.pages.create(parent={"database_id": database_id}, properties=new_page)

def index(request):
    if request.method == "POST":
        # フォームから送信されたISBNを取得
        isbn = request.POST["isbn"]

        # ISBNから書籍情報を取得
        book_info = get_book_info(isbn)

        if not book_info:
            return JsonResponse({"error": "Book not found"}, status=404)

        book = Book(
            title=book_info["title"],
            author=book_info["author"],
            isbn=isbn,
            cover_image_url=book_info["cover_image_url"],
        )

        # Notion APIを使ってNotionのデータベースに登録
        notion_database_id = "5021d8710daf4545b158e587e4c9dc98" #"your_notion_database_id_here"
        add_book_to_notion(notion_database_id, book)

        return JsonResponse({"success": "Book added to Notion"}, status=200)

    # GETリクエストの場合、空のフォームを表示
    return render(request, "my_app/index.html")
