"""
This module defines the classes needed to process a 730DC newsletter url
"""

import requests
from uuid import uuid4

from bs4 import BeautifulSoup, Tag


class Blurb:
    def __init__(self, order: int = 0, title: str = "", body: list = [], b_type: str = ""):
        self.id = uuid4()
        self.order = order
        self.title = title
        self.body = body
        self.b_type = b_type

    def __str__(self):
        return (f"Blurb (ID: {self.id}, Type: {self.b_type}, Title: '{self.title}')")


class NlHandler:

    def __init__(self, url: str):
        self.url = url
        self.content = self._nl_content()
        self.weekly_s, self.markers = self._get_markers()
        

    def _nl_content(self) -> BeautifulSoup:
        """
        Gets the content of the webpage 
        from the url given as an argument.
        """
        
        # consider using SoupStrainer to save effort later
        data = requests.get(self.url)
        content = BeautifulSoup(data.content, 'html.parser', )
        return content
    

    def _get_markers(self) -> dict:
        """
        Create the markers (bs4.Tag objects) used to triangulate a Blurb.type. 
        """
        weekly_s = False
        marker_dict = {}

        img_url = [
            # what to know
            ("wtk", "https://gallery.mailchimp.com/576dfd24a3c9e732d2920f811/images/99c7afbf-22e1-485a-befa-77bfa4c09cc1.png"),
            # what to do
            ("wtd", "https://gallery.mailchimp.com/576dfd24a3c9e732d2920f811/images/686d06ad-1691-48c9-af9d-ec5766c203e3.png"),
            # weekly scheduler
            ("ws", "https://gallery.mailchimp.com/576dfd24a3c9e732d2920f811/images/6e6f9b72-2610-49ae-9332-3ec026982100.png")
        ]

        for img in img_url:
            try:
                marker = self.content.find_all(name="img", src=img[1])
                marker = marker[0]
            
            # catch when the marker isn't in the newsletter
            except IndexError:
                print(f"Error: {img[0].upper()} image marker not found for {self.url}")
                continue
            
            if img[0] == "wtk":
                marker_dict["wtk"] = marker
            elif img[0] == "ws": 
                weekly_s = True
                marker_dict["wtd"] = marker
            
        return weekly_s, marker_dict


    def _get_blurb_type(self, tag: Tag) -> str:
        # Identify if blurb is an ad, wtk, or wtd
        if tag in self.markers["wtk"].find_all_previous(f"{tag.name}"):
            return "AD"
        elif tag in self.markers["wtd"].find_all_previous(f"{tag.name}"):
            return "WTK"
        else:
            return "WTD"


    def _get_body(self, tag: Tag) -> list:
        # get the body of the blurb and any sub-bullets
        text = []
        main_body = tag.find_next_sibling("h4").get_text()
        bullet = tag.find_next_sibling("ul")
        if main_body:
            if bullet:
                # print(bullet.find_all("h4").get_text())
                main_body = main_body + bullet.h4.get_text()
                text.append(main_body)
            else:
                text.append(main_body)
        elif bullet:
            # print(bullet.h4.get_text())
            text.append(bullet.h4.get_text())
        else:
            print("Error. No text body or bullets found.")
        return text


    def check_h1(self, h1: Tag):
        
        # create a recursive func for checking parent
        def check_parent(tag: Tag) -> bool:
        
            parent = tag.parent
            p_class_ = parent.get("class")
            
            # in case it runs all the way up the html doc for some reason
            if parent.name == "html":
                return False
            
            # no class attribute
            if p_class_ is None:
                return check_parent(parent)
            
            # actual base cases
            if p_class_ == ["mcnBoxedTextBlock"]:
                return False
            elif p_class_ == ["mcnTextBlock"]:
                return True

            # continue recursion
            return check_parent(parent)
        
        # there is always a None sibling so do the next sibling after that
        sib = h1.next_sibling.next_sibling
        # see if it's boxed
        check = check_parent(h1)
        

        if sib.name == "h4" or sib.name == "p" or sib.name == "ul":
            if check == True:
                return True
            else:
                print("TAG WAS BOXED")
        else:
            print("CHECK FALSE FOR: ", h1.get_text(), sib.name)
        
        # if sib.name:
        #     if check == True:
        #         return True
        #     else:
        #         return False
        # else:
        #     print("CHECK FALSE FOR: ", h1.get_text(), sib.name)
        #     return False
    
    # def check_h4(self, h4: Tag):


    def _get_h1_h4(self):

        # if weekly scheduler is False
        def no_ws():

            for tag in text:
                if tag.name == "h1":
                    if self.check_h1(h1=tag):
                        titles.append(tag)
                        continue
                continue
            return titles

        # if weekly scheduler is True
        def ws():

            for tag in text:
                if tag.name == "h1":
                    if self.check_h1(h1=tag):
                        titles.append(tag)
                        continue
                    continue
                if tag.contents[0].name == "strong":
                    titles.append(tag)
                    continue
            return titles
        

        text = self.content.find_all(["h1", "h4"])
        titles = []

        if self.weekly_s == True:
            title_list = ws()
            # for t in title_list:
            #     print(t.get_text())    
        else:
            title_list = no_ws()
            # for t in title_list:
            #     print(t.get_text())
        return title_list

    def _breakout_blurbs(self):
        """
        """

        # call _get_tables()

        # find the h1's of the blurbs needed to check
        b_titles = self.content.find_all("h1")
       
        # Build the Blurb and make a list
        blurb_count = 1
        
        for tag in b_titles:
            blurb = Blurb()
            blurb.order = blurb_count
            blurb.title = tag.get_text()
            blurb.body = self._get_body
            blurb.b_type = self._get_blurb_type(tag=tag)
            blurb_count += 1
            print(blurb)


    def __str__(self):
        return (f"NLHandler (Newsletter: '{self.content.title.get_text()}')")


# TEST
if __name__ == "__main__":
    
    url_list = [
        "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=c35f0dd0aa",
        
        # For url below, test Thursday newsletter with changed WTD titles
        "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=ec7673a6f4",
        
        # For url below, see if the font size mistake makes a difference
        "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=63b262de00",
        
        # For the url below, need to add a 'weekly scheduler' img marker for when there is no wtd marker
        "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=04ac2c19ea"
    ]
    
    # num of titles in each url above
    answers = [8, 18 , 13, 28]

    for url, answer in zip(url_list,answers):
        handler = NlHandler(url=url)
        test = handler._get_h1_h4()
        try:
            len(test)
        except TypeError:
            print("TEST ERRORED/INCOMPLETE")
            continue
        if len(test) == answer:
            print("TEST PASSED")
        else:
            print("TEST FAILED")
        # test results

        print("-------------------------------------------------")
