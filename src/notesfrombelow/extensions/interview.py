import re

import markdown
import xml.etree.ElementTree as etree


INTERVIEW_RE = r'^~(?P<author>[A-Z]{1,3})(?P<number>[1-5]) '
class InterviewPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        """
        ~A1 Text here (on the left, first colour)
        ~B2 Text here (on the right, second colour)
        ~C3 Text here (on the right, third colour)
        ~D4 Text here (on the right, fourth colour)
        ~D5 Text here (on the right, fifth colour)
        """
        author = m.group('author')
        number = m.group('number')
        el = etree.Element('span')
        el_class = 'interview-quote author-' + number
        el.set('class', el_class)
        el.text = author
        return el


class InterviewExtension(markdown.Extension):
    def extendMarkdown(self, md):
        # A recent Markdown update changed the syntax for registering new inline patterns. I'm only guessing here. The last parameter is a priority number I guess
        md.inlinePatterns.register(InterviewPattern(INTERVIEW_RE, self), 'interview', 175)


def makeExtension(*args, **kwargs):
    return InterviewExtension(*args, **kwargs)

