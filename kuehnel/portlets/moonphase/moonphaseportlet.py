
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever

from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
from zope import schema
from zope.formlib import form
from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
from zope.i18nmessageid import ZopeMessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner
from time import localtime
from urllib import urlencode
from uuid import uuid4

# TODO: If you require i18n translation for any of your schema fields below,
# uncomment the following to import your package MessageFactory
#from kuehnel.portlets.moonphase import MoonphasePortletMessageFactory as _


class IMoonphasePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    instanceid = schema.TextLine(title=_(u"unique id of this portlet"),
                                  description=_(u"ids of moonphase portlets should be unique throughout a site"),
                                  default=u"default",
                                  required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMoonphasePortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    instanceid = uuid4().hex

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, instanceid=uuid4().hex):
        if not instanceid or instanceid == "default":
            instanceid=uuid4().hex
        print "assignment init called, portlet id %s" % instanceid
        self.instanceid = instanceid

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Moonphase Portlet"


TEMPLATE = u"""
jQuery(function($){
  function LinkHandler(event) {
  var params = { "year:int" : 0 };
    params["year:int"]  = $("#year-%(instanceid)s").text();
    var urlparam = "%(urlstring)s&" + jQuery.param(params) + " #%(instanceid)s";
    $("#moonphasewrapper-%(instanceid)s").load(urlparam);
  return false;};
  $("#moonphasewrapper-%(instanceid)s").on("click", "#moonphasePreviousLink",{foo: "Meldung"}, LinkHandler);
});
"""
#"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render_template = ViewPageTemplateFile('moonphaseportlet.pt')
    def render(self):
        print "renderer render called"
        #self.instanceid = self.getInstanceId()
        return self.render_template()

    def update(self):
        print "renderer update called"
        context = aq_inner(self.context)
        request = self.request
        if self.request.form.has_key("direction"):
            self.year = request.form.get("year") - 1
        else:
            self.now = localtime()
            self.year = self.now[0]
        
    def getPreviousYear(self, year):
        return year-1

    def getPortletById(self):
        context = self.context.aq_inner
        params = self.getPortletMetadata()
        if not params:
            print "cannot get portlet metadata in gePortletById"
            return None
        manager = getUtility(IPortletManager, name=params["portletManager"], context=context)
        retriever = getMultiAdapter((context, manager,), IPortletRetriever)            
        for assignment in retriever.getPortlets():
            if assignment["key"] == params["portletKey"] and assignment["name"] == params["portletName"]:
                return assignment["assignment"]
        return None
        
    def getPortletMetadata(self):
        if hasattr(self, "__portlet_metadata__"):
            params = dict(
                portletName=self.__portlet_metadata__["name"],
                portletManager=self.__portlet_metadata__["manager"],
                portletKey=self.__portlet_metadata__["key"],)
            print "got urlparamaters from __portlet_metadata__"
        else:
            if self.request.form.has_key("portletName"):
                params = dict(
                    portletName=self.request.form.get("portletName"),
                    portletManager=self.request.form.get("portletManager"),
                    portletKey=self.request.form.get("portletKey"),
                    )
                print "got urlparamaters from request"
            else:
                print "cannot get __portlet_metadata__"            
                return {}
        return params
    
    def getUrlParamsMetadata(self):
        return urlencode(self.getPortletMetadata())

    def getInstanceId(self):
        assignment = self.getPortletById()
        if assignment:
            return assignment.instanceid
        else:
            return None
        
    def getJsSnippet(self):
        urlstring = '%s/@@refreshMoonphase?direction:string=previous&portletId:string=%s&%s' % \
                    (self.request['ACTUAL_URL'], self.getInstanceId(), self.getUrlParamsMetadata())
        
        js = TEMPLATE % {"instanceid": self.getInstanceId(), "urlstring": urlstring}
        return js

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMoonphasePortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMoonphasePortlet)
