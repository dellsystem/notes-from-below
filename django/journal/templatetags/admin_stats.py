import calendar
import datetime

from django import template
from django.urls import reverse
from django.utils.html import format_html

from journal.models import Article, Issue


register = template.Library()


@register.simple_tag
def show_articles():
    first_calendar, articles = show_article_calendar(0)
    second_calendar, articles_2 = show_article_calendar(1)

    recent_html = []
    for article in articles + articles_2:
        title = article.title
        if len(title) > 30:
            title = title[:30] + '...'
        recent_html.append(
            '<div class="item"><a href="{url}">{title}</a> ({date})</a></div>'.format(
                url=reverse('editor:journal_article_change', args=[article.pk]),
                title=title,
                date=article.date.strftime('%b %-d'),
            )
        )

    recent_articles = ''.join(recent_html)

    # Upcoming articles = not yet published, and not attached to an issue
    upcoming_articles = Article.objects.filter(published=False, issue=None)
    if upcoming_articles.exists():
        upcoming_articles_html = []
        for article in upcoming_articles:
            title = article.title
            if len(title) > 30:
                title = title[:30] + '...'
            upcoming_articles_html.append(
                '<div class="item"><a href="{url}">{title}</a> ({date})</a></div>'.format(
                    url=reverse('editor:journal_article_change', args=[article.pk]),
                    title=title,
                    date=article.date.strftime('%b %-d'),
                )
            )
        upcoming_html = format_html("""
            <h3>Upcoming</h3>
            <div class="ui bulleted list">
                {upcoming_articles}
            </div>
            """.format(
                upcoming_articles=''.join(upcoming_articles_html)
            )
        )
    else:
        upcoming_html = '<h3>No upcoming articles</h3>'

    return format_html("""
        <div class="ui aligned stackable grid">
            <div class="ui four wide column">
                <h3>Recent</h3>
                <div class="ui bulleted list">
                    {recent_articles}
                </div>
                {upcoming}
            </div>
            <div class="ui six wide column">
                {first_calendar}
            </div>
            <div class="ui six wide column">
                {second_calendar}
            </div>
        </div>
    """.format(
        recent_articles=recent_articles,
        upcoming=upcoming_html,
        first_calendar=first_calendar,
        second_calendar=second_calendar,
    ))


def show_article_calendar(month_delta=0):
    # TODO: This needs to be cleaned up ... pass current date as param?
    today = datetime.date.today()
    # If we're in the first half of the month, show the previous month and not
    # the next month.
    if today.day < 15:
        month_delta -= 1

    current_month = (today.month + month_delta) % 12
    if current_month == 0:
        current_month = 12
    current_year = today.year + (today.month + month_delta == 13)
    current_day = today.day

    num_non_days, num_days = calendar.monthrange(current_year, current_month)
    non_days_html = format_html('<div class="column"></div>' * num_non_days)
    column_i = num_non_days
    days_html = []
    all_articles = []
    for i in range(num_days):
        day = i + 1
        date = datetime.date(current_year, current_month, day)
        articles = Article.objects.filter(date=date, issue=None)
        article_titles = []
        for article in articles:
            title = article.title
            if len(title) > 32:
                title = title[:30] + '...'
            article_titles.append(title)
            all_articles.append(article)

        if date == today:
            if article_titles:
                colour = 'orange'
            else:
                colour = 'yellow'
        else:
            if article_titles:
                if date > today:
                    colour = 'red'
                else:
                    colour = 'grey'
            else:
                # No articles so no colour.
                colour = ''

        if column_i == 6:
            row_end_html = '</div><div class="row">'
            column_i = 0
        else:
            column_i += 1
            row_end_html = ''
        days_html.append(
            """
                <div class="{colour} column" title="{articles}">
                    {day}
                </div>
                {row}
            """.format(
                colour=colour,
                day=day,
                articles=format_html(' / '.join(article_titles)),
                row=row_end_html,
            )
        )

    dow_headings_html = format_html(
        '<div class="row">{}</div>'.format(
            ''.join(
                '<div class="column"><strong>{}</strong></div>'.format(dow)
                for dow in calendar.weekheader(1).split()
            )
        )
    )

    calendar_html = format_html(
        """
        <h2>{current_month} {current_year}</h1>
        <div class="ui celled seven column stackable grid calendar">
            {dow_headings}
            <div class="row">
            {non_days}
            {days}
            </div>
        </div>
        """,
        current_year=current_year,
        current_month=calendar.month_name[current_month],
        non_days=non_days_html,
        dow_headings=dow_headings_html,
        days=format_html(''.join(days_html)),
    )
    return calendar_html, all_articles


@register.simple_tag
def show_issues():
    today = datetime.date.today()

    months_html = []
    date = datetime.date(2018, 1, 1)
    column_i = 0  # for rows
    while date <= today:
        issues = Issue.objects.filter(date__month=date.month, date__year=date.year)
        date_display = date.strftime('%b %Y')

        if issues.exists():
            # Assume there can be only one issue per month.
            issue = issues.latest()
            if issue.published:
                colour = 'grey'
            else:
                colour = 'red'

            month_html = """
                <div class="{colour} column">
                    <h4 class="ui inverted header">
                        {date} - {number}
                        <a href="{url}" class="sub header">
                            {title}
                        </a>
                    </h4>
                </div>
            """.format(
                colour=colour,
                title=issue.title,
                date=date_display,
                number=issue.number,
                url=reverse('editor:journal_issue_change', args=[issue.pk]),
            )
        else:
            month_html = '<div class="column">{}</div>'.format(date_display)

        months_html.append(month_html)

        if column_i == 5:
            column_i = 0
            months_html.append('</div><div class="row">')
        else:
            column_i += 1

        if date.month == 12:
            date = date.replace(month=1, year=date.year + 1)
        else:
            date = date.replace(month=date.month + 1)

    return format_html(
        """
        <div class="ui celled six column doubling grid calendar">
            <div class="row">
            {months}
            </div>
        </div>
        """.format(
            months=''.join(months_html),
        )
    )
