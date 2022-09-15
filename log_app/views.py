from datetime import datetime
import codecs
from user_app.models import TblUser

# Create your views here.
def log_text(action, user, header, author_id, language, text_type):
    
    try:
        f = codecs.open('log_text.log', 'x', "utf-16")
        f.write('action\tuser\theader\tauthor\tlanguage\ttext_type\tdata_create\n')
    except FileExistsError:
        f = codecs.open('log_text.log', 'a', "utf-16")
    
    author = TblUser.objects.filter(id_user=author_id)
    if len(author) == 0:
        f.write('{0}\t{1} {2}({3})\t{4}\tNone\t{5}\t{6}\t{7}\n'.format(action, user.last_name, user.name, user.login, header, language, text_type, datetime.now().strftime('%d.%m.%y %H:%M:%S')))
    else:
        author = author.first()
        f.write('{0}\t{1} {2}({3})\t{4}\t{5} {6}({7})\t{8}\t{9}\t{10}\n'.format(action, user.last_name, user.name, user.login, header, author.last_name, author.name, author.login, language, text_type, datetime.now().strftime('%d.%m.%y %H:%M:%S')))
    
    f.close()