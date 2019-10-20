import dropbox
import base64

def upload_image(img_binary, file_name):

    ACCESS_TOKEN = os.environ["D_ACCESS_TOKEN"]
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    path = '/static/image/' + file_name

    dbx.files_upload(img_binary, path)

    setting = dropbox.sharing.SharedLinkSettings(
        requested_visibility=dropbox.sharing.RequestedVisibility.public)
    link = dbx.sharing_create_shared_link_with_settings(
        path=path, settings=setting)

    links = dbx.sharing_list_shared_links(path=path, direct_only=True).links
    if links is not None:
        for link in links:
            url = link.url
            url = url.replace(
                'www.dropbox',
                'dl.dropboxusercontent').replace(
                '?dl=0',
                '')
            return url
