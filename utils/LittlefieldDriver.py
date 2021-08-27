import mechanize

class LittlefieldDriver:
    '''
    A driver for the Littlefield simulation game that can access
    & interact with the game state.

    Inspired by the code & methttps://op2.responsive.net/Littlefield/Plot?data=JOBQ&x=allhodology from Greg Lewis's 2017 Medium post
    about connecting Littlefield data to Tableau via Python

    @Author: Spencer Elkington
    '''

    def __init__(self, config, secrets):
        
        # Initialize web driver & login
        self.browser: mechanize.Browser = mechanize.Browser()
        self.browser.open(secrets["LITTLEFIELD_ADDRESS"])

        self.browser.select_form(nr=0)
        self.browser.form['id'] =       str(secrets["LITTLEFIELD_USERNAME"])
        self.browser.form['password'] = str(secrets["LITTLEFIELD_PASSWORD"])
        self.browser.submit()

        self.browser.open(f'{config["GAME_ADDRESS"]}/CheckAccess')
        print(self.browser)