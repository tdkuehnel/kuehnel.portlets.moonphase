# -*- coding: UTF-8 -*-
from zope.interface import implements
from Products.Five.browser import BrowserView
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever

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
        print "refreshment of moonphase portlet"

        content = self.context.aq_inner
        #content = self.context

        print " "
        print self.context
        name = self.request.form.get("portletName")
        managername = self.request.form.get("portletManager")
        key = self.request.form.get("portletKey")

        print name, managername, key
        portlet = self.getPortletById(content, managername, key, name)
        
        manager = self.getPortletManager(managername)

        managerRenderer = manager(content, self.request, self)
        renderer = managerRenderer._dataToPortlet(portlet.data)

        renderer.update()
                
        return renderer.render()
    
