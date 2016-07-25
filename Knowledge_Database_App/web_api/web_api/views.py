from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('web_api')


def my_view(request):
    return {'project': 'web_api'}
