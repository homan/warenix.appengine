class View():

	def html_head_div(self):
		html = """
		<div id="head" class="head">
	                <div id="logo" class="frame">
	                </div>
	                <div id="search_form" class="frame">
							<form method="get" action="http://apps.facebook.com/mystatussearch/" method="get" target="_top"/>

	                                <div id="search_field" class="search ">
	                                        <div class="search frame">
	                                        <input type="checkbox" checked="true" name="check_status" value="yes">status</input><br/>
	                                        <input type="checkbox" checked="true" name="check_comment" value="yes">comment</input><br/>

											<select class="search" name="check_period" size="1">
												<option value="0">anytime</option>
												<option value="86400">1 day</option>
												<option value="604800">1 week</option>
												<option value="2678400" selected="selected">1 month</option>
											</select>
	                                        </div>

	                                        <button class="btn" title="Submit Search"></button>
	                                        <input class="box" type="text" name="keyword"></input>
	                                </div>
	                        </form>
	                </div>
	        </div>
		"""

		return html

	def html_head(self):
		html = """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>My Status Search</title>
<link rel="stylesheet" href="style.css" type="text/css"/>
</head>
		"""

		return html

	def html_begin_content_div(self, heading):
		html = """
        <div class="content frame">
        <h3>%(heading)s</h3>
        <ul>
        """ % {
        	'heading' : heading
        }
       		return html

        def html_end_content_div(self):
        	html = """
        </ul>
        </div>
		"""
		return html

	def html_search_result(self, avatar_url, post_date, message_url, message_text):
		html = """
	                <li class="frame result">
	                        <img class="avatar" src='%(avatar_url)s'/>
	                        <b class="post_date">%(post_date)s</b>
	                        <a  class="message" href='%(message_url)s' target='_top'>%(message_text)s</a>
	                </li>
		""" % {
			'avatar_url' : avatar_url,
			'post_date' : post_date,
			'message_url' : message_url,
			'message_text' : message_text,
		}
		return html
	def html_begin_body(self):
		html = """
		<body class="frame">
		"""
		return html

	def html_end_body(self):
		html = """
		</body>
		</html>
		"""
		return html


"""
v = View()
self.out v.html_head()
self.out v.html_begin_body()

self.out v.html_head_div()


self.out content div - status
self.out v.html_begin_content_div(heading="Searching status message found 3 result")

self.out v.html_search_result(
avatar_url="http://profile.ak.fbcdn.net/profile6/1492/105/q671679020_3973.jpg",
post_date="today",
message_url="http://some.html",
message_text="hi",
)
self.out v.html_search_result(
avatar_url="http://profile.ak.fbcdn.net/profile6/1492/105/q671679020_3973.jpg",
post_date="today",
message_url="http://some.html",
message_text="hi",
)

self.out v.html_end_content_div()


self.out v.html_end_body()
"""
