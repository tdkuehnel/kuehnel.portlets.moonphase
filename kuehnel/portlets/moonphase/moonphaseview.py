# -*- coding: UTF-8 -*-
from zope.interface import implements
from Products.Five.browser import BrowserView
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever

import logging

class MoonphaseView(BrowserView):

    # --
    # Moonphase in-place refreshment via ajax call.
    # The display state of the portlet is held only on the client side - we can have multiple clients
    # asking for update. This view does not need to know which portlet assignment is involved,
    # it calculates the display data according to provided request variables coming from the client side.
    #
    # Nevertheless we need some way to find our portlet class from here.
    # --

    def __call__(self):
        return self.render()
    
    def getPortletById(self, content, portletManager, key, name):
        manager = getUtility(IPortletManager, name=portletManager, context=content)
        retriever = getMultiAdapter((content, manager,), IPortletRetriever)

        print "getPortletById:  ",content, portletManager, key, name
        print "iterating portlet assignements"
        for assignment in retriever.getPortlets():
            print assignment["key"], assignment["name"]
        for assignment in retriever.getPortlets():
            if assignment["key"] == key and assignment["name"] == name:
                return assignment["assignment"]
            
        return None
    
    def getPortletManager(self, column):
        manager = getUtility(IPortletManager, name=column)
        return manager
    
    def render(self):
        logger = logging.getLogger("Plone")
        print " "
        print "refreshment of moonphase portlet"

        content = self.context.aq_inner
        #content = self.context
        #import pdb; pdb.set_trace()
            
        context_state = getMultiAdapter((content, self.request), name=u'plone_context_state')
        print self.context, "is default page: %s" % context_state.is_default_page(), self.context.default_page
        name = self.request.form.get("portletName")
        managername = self.request.form.get("portletManager")
        key = self.request.form.get("portletKey")

        print name, managername, key
        portlet = self.getPortletById(content, managername, key, name)
        if not portlet:
            # let's try to find it assigned on the default_page view
            defaultpage = getattr(content,getattr(content,"default_page",None),None)
            if defaultpage:
                portlet = self.getPortletById(defaultpage, managername, key, name)
                content = defaultpage
            else:
                logger.warn('cannot find an assignment for a portlet of type %s in ajax update request' % name)
                return None            
            
        manager = self.getPortletManager(managername)

        managerRenderer = manager(content, self.request, self)
        renderer = managerRenderer._dataToPortlet(portlet.data)

        renderer.update()
                
        return renderer.render()
    
