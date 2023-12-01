from . import View
from utils.data import icons

import discord


class Paginator(View):
	def __init__(self, invoke: discord.Interaction, bot, pages: list[discord.Embed], wrap: bool = False):
		super().__init__(view_inter=invoke)
		self.invoke = invoke
		self.bot = bot
		self._page = 0
		self._pages = pages
		self.original_message = None
		self._wrap = wrap
		self._footers = []

		if not self._wrap:
			self.children[0].disabled = True

	async def update(self, page):
		if not self.original_message:
			self.original_message = await self.invoke.original_response()

		if not self._wrap:
			if self._page + 1 == len(self._pages):
				self.children[1].disabled = True
			else:
				self.children[1].disabled = False
	
			if self._page == 0:
				self.children[0].disabled = True
			else:
				self.children[0].disabled = False

		page.set_footer(
			text=f"{self._footers[self._page] if self._footers[self._page] else ''}\n{self._page + 1}/{len(self._pages)}",
			icon_url=page.footer.icon_url)
		await self.original_message.edit(embed=page, view=self)

	def _check_embed(self, page):
		if not isinstance(page, discord.Embed):
			raise TypeError("Page must be a discord.Embed")

		self._footers.append(page.footer.text)
		page.set_footer(
			text=f"{self._footers[self._page] if self._footers[self._page] else ''}\n{self._page + 1}/{len(self._pages)}",
			icon_url=page.footer.icon_url)
	
	@discord.ui.button(emoji=icons.page_left, style=discord.ButtonStyle.blurple)
	async def back(self, interaction, button):
		self._page = self._page - 1 if self._page > 0 else (len(self._pages) - 1 if self._wrap else 0)
		await self.update(self._pages[self._page])
		await interaction.response.defer()

	@discord.ui.button(emoji=icons.page_right, style=discord.ButtonStyle.blurple)
	async def forward(self, interaction, button):
		self._page = self._page + 1 if self._page < len(self._pages) - 1 else (0 if self._wrap else len(self._pages) - 1)
		await self.update(self._pages[self._page])
		await interaction.response.defer()

	async def start(self):
		[self._check_embed(page) for page in self._pages]
		
		self.original_message = await self.invoke.response.send_message(embed=self._pages[self._page], ephemeral=True, view=self)
