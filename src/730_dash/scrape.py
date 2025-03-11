"""
This module defines the classes needed to process a 730DC newsletter url
"""

import requests

from bs4 import BeautifulSoup, Tag


class Blurb:
    def __init__(self, order: int = 0, title: str = "", body: str = "", b_type: str = ""):
        self.order = order
        self.title = title
        self.body = body
        self.b_type = b_type

    def __str__(self):
        return (f"Blurb (Order: {self.order}, Title: '{self.title}', Type: {self.b_type})")

class NlHandler:

    def __init__(self, url: str):
        self.url = url
        self.content = self._nl_content()
        self.markers = self._get_markers()
        

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
        

        # what to know
        wtk_marker = self.content.find_all(name="img", 
                                src="https://gallery.mailchimp.com/576dfd24a3c9e732d2920f811/images/99c7afbf-22e1-485a-befa-77bfa4c09cc1.png")
        wtk_marker = wtk_marker[0]

        # what to do
        wtd_marker = self.content.find_all(name="img", 
                                src="https://gallery.mailchimp.com/576dfd24a3c9e732d2920f811/images/686d06ad-1691-48c9-af9d-ec5766c203e3.png")
        wtd_marker = wtd_marker[0]

        return {
            "wtk": wtk_marker,
            "wtd": wtd_marker
            }


    def check_tag(self, tag: Tag):
        # find where the blurb belongs
        if tag in self.markers["wtk"].find_all_previous(f"{tag.name}"):
            return "AD"
        elif tag in self.markers["wtd"].find_all_previous(f"{tag.name}"):
            return "WTK"
        else:
            return "WTD"


    def _get_body(self, tag):
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

    def _breakout_blurbs(self):
        """
        """

        # find the h1's of the blurbs needed to check
        b_titles = self.content.find_all("h1")
       
        # Build the Blurb
        blurb_count = 1
        
        for tag in b_titles:
            blurb = Blurb()
            blurb.order = blurb_count
            blurb.title = tag.get_text()
            blurb.body = self._get_body
            blurb.b_type = self.check_tag(tag=tag)
            blurb_count += 1
            print(blurb)


    def __str__(self):
        return (f"NLHandler (Newsletter: '{self.content.title.get_text()}')")


if __name__ == "__main__":
    # testing
    url = "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=c35f0dd0aa"
    # url = "https://us7.campaign-archive.com/?u=576dfd24a3c9e732d2920f811&id=ec7673a6f4"
    handler = NlHandler(url=url)
    handler._breakout_blurbs()
