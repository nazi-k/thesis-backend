from enum import Enum


class IssueType(str, Enum):
    TASK = 'task'
    BUG = 'bug'
    STORY = 'story'


class IssueStatus(str, Enum):
    BACKLOG = 'backlog'
    SELECTED = 'selected'
    INPROGRESS = 'inprogress'
    DONE = 'done'


class IssuePriority(str, Enum):
    HIGHEST = '5'
    HIGH = '4'
    MEDIUM = '3'
    LOW = '2'
    LOWEST = '1'
