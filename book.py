"""
"""
import json
import pprint
import random
import requests
import time

from bs4 import BeautifulSoup

class Book:
	title = ""
	by_similarity = {}
	by_list = {}
	authors = [""]
	pages = 0
	publish_date = ""
	description = ""

	WEBSITE = "https://www.goodreads.com"
	url = ""
	similarity_url = ""
	list_url = ""

	def __init__(self, title):
		self.title = title
		self.by_similarity = {}
		self.by_list = {}
		self.authors = [""]
		self.pages = 0
		self.publish_date = ""
		self.description = ""
		self.url = ""
		self.similarity_url = ""
		self.list_url = ""

	def numbered_choices(self, lists):
		"""
		Has the user choose a number corresponding a
		list of choices shown on screen.
		"""
		looping = True
		while looping:
			for position, result in enumerate(lists):
				print(position, result.text)
				print()
			choice = input("Enter a number: ")
			try:
				choice = int(choice)
				if choice < len(lists):
					return choice
				else:
					print("It must be a listed number.")
			except Exception:
				print("It must be a listed number.")

	def numbered_lists(self, lists):
		"""
		Similar to Numbered Choices, except it doesn't have
		them choose anything. Simply displays the list.
		"""
		the_list = []
		for position, result in enumerate(lists):
			print(position, result.text)
			print()
			the_list.append(result.text)
		return the_list

	def search(self):
		"""
		Searches the goodreads database for a book whose title
		corresponds to the name given.
		"""

		page = requests.get(self.WEBSITE + "/search?q=" + self.title.replace(" ", "+"))
		print(page.url)
		bs_page = BeautifulSoup(page.text, features="html.parser")
		book_list = bs_page.findAll("a", {"class": "bookTitle"})
		choice = self.numbered_choices(book_list)
		self.url = self.WEBSITE + book_list[choice].get("href").split("?")[0]
		self.title = book_list[choice].text

	def get_information(self):
		"""
		Gets information such as authors, publish date, pages,
		and description.
		"""

		time.sleep(random.randint( 1, 3))

		page = requests.get(self.url)
		bs_page = BeautifulSoup(page.text, features="html.parser")

		# Get description.
		desc_tag = bs_page.findAll("div", {"id": "description"})
		if len(desc_tag) >= 1:
			desc_tag = desc_tag[0]
			if "...more" in desc_tag.text:
				self.description = desc_tag.text.split("...more")[0]
			else:
				self.description = desc_tag.text
			print(self.description)

		# Get Authors.
		authors_tag = bs_page.findAll("a", {"class": "authorName"})
		self.authors = self.numbered_lists(authors_tag)
		print(self.authors)

		# Get Publish Date.
		pub_tag = bs_page.findAll("div", {"class": "row"})
		for position, result in enumerate(pub_tag):
			if "Published" in result.text:
				self.publish_date = result.text
				print(self.publish_date)

		# Get Pages.
		page_tag = bs_page.findAll("span", {"itemprop": "numberOfPages"})
		if len(page_tag) >= 1:
			page_tag = page_tag[0]
			self.pages = int(page_tag.text.split(" ")[0])
			print(self.pages)

	def find_by_similar(self):
		"""
		Creates a list of books and corresponding authors
		based on similarity to the main book.
		"""
		
		time.sleep(random.randint( 1, 3))

		page = requests.get(self.url)
		bs_page = BeautifulSoup(page.text, features="html.parser")

		# Find similar books page.
		link = bs_page.findAll("a", {"class": "seeMoreLink"})
		if len(link) >= 1:
			link = link[0]
			if "https://" in link.get("href"):
				new_page = requests.get(link.get("href"))
			else:
				new_page = requests.get(self.WEBSITE + link.get("href"))
			bs_new_page = BeautifulSoup(new_page.text, features="html.parser")

			time.sleep(random.randint( 1, 3))

			# Get list of books.
			risuto_titles = bs_new_page.findAll("a", {"class": "gr-h3 gr-h3--serif gr-h3--noMargin"})
			risuto_author = bs_new_page.findAll("span", {"itemprop": "author"})

			for position, result in enumerate(risuto_titles):
				self.by_similarity[risuto_titles[position].text] = risuto_author[position].text

	def find_by_lists(self):
		"""
		Creates a list of books that share a list with the main
		book.
		"""
		

		time.sleep(random.randint( 1, 3))

		page = requests.get(self.url)
		bs_page = BeautifulSoup(page.text, features="html.parser")

		# Go to list of lists page.
		list_of_lists_link = bs_page.findAll("a", {"class": "actionLink", "style": "float:right"})
		if len(list_of_lists_link) >= 1:
			list_of_lists_link = list_of_lists_link[0]
			lol_page = requests.get(self.WEBSITE + list_of_lists_link.get("href"))
			bs_lol_page = BeautifulSoup(lol_page.text, features="html.parser")

			# Go to each list page.
			lists = bs_lol_page.findAll("a", {"class": "listTitle"})

			for position, result in enumerate(lists):
				time.sleep(random.randint( 1, 3))
				# Get list of books.
				self.by_list[result.text] = {}
				list_page = requests.get(self.WEBSITE + result.get("href"))
				bs_list_page = BeautifulSoup(list_page.text, features="html.parser")

				risuto_titles = bs_list_page.findAll("a", {"class": "bookTitle"})
				risuto_author = bs_list_page.findAll("a", {"class": "authorName"})

				for position2, result2 in enumerate(risuto_titles):
					self.by_list[result.text][risuto_titles[position2].text] = risuto_author[position2].text

	def create_json(self):
		"""
		Creates json file with similar books.
		"""
		with open(self.title + ".json", "w") as JSON:
			full = []
			full.append(self.by_similarity)
			full.append(self.by_list)
			similar_json = json.dump(full, JSON, indent=4)


def find_book(title):
	"""
	Creates a book object and uses its functions
	to create a file with a list of similar books.
	"""

	my_book = Book(title)

	my_book.search()
	my_book.get_information()

	my_book.find_by_similar()
	my_book.find_by_lists()

	my_book.create_json()


# find_book("Ultralearning")









# for i in my_book.by_list:
		
	# 	for j in my_book.by_list[i]:
	# 		my_book.by_list[i][j].replace("\n", " ")
	# 		print(my_book.by_list[i][j])
	# print()
	# print()
	# for i in my_book.by_similarity:
	# 	print(my_book.by_similarity[i])