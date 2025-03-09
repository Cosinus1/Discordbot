import discord
from discord.ui import View
from classes.item_ui import ItemButton
from classes.shop_manager import shop_manager

class ShopUI(View):
    """
    A view for displaying all items in the shop, organized in columns.
    """

    def __init__(self):
        super().__init__()
        self.items = shop_manager.items
        self.potions = shop_manager.potions
        
        # Organize items into rows (5 items per row, maximum of 5 rows)
        # Discord has a limit of 25 components per view
        all_items = self.items + self.potions
        displayed_items = all_items[:25]  # Take at most 25 items
        
        # Organize by rows instead of columns for better UI
        rows = [displayed_items[i:i + 5] for i in range(0, len(displayed_items), 5)]
        
        # Add ItemButton components for each item
        for row_idx, row_items in enumerate(rows):
            for item in row_items:
                item_button = ItemButton(item, context="shop", shop_ui=self)  # Pass shop_ui reference
                item_button.row = row_idx  # Set the row for this button
                self.add_item(item_button)

    async def send_shop(self, ctx):
        """Send the shop UI to the channel."""
        # Get user data to show available gold
        from database import get_user_data
        user = get_user_data(ctx.author.id)
        
        description = "Browse the available items below."
        if user and "money" in user:
            description += f"\n\nYour Gold: **{user['money']}**"
        
        embed = discord.Embed(
            title="Shop",
            description=description,
            color=discord.Color.blue()
        )
        
        # Add item categories count
        item_types = {}
        all_items = self.items + self.potions
        for item in all_items:
            item_type = item.get("type", "misc")
            item_types[item_type] = item_types.get(item_type, 0) + 1
            
        for item_type, count in item_types.items():
            embed.add_field(name=f"{item_type.title()}s", value=f"{count} available", inline=True)
        
        # Add note if shop has more items than can be displayed
        if len(all_items) > 25:
            embed.set_footer(text=f"Showing 25/{len(all_items)} items. Use !shop2 to see more.")
            
        await ctx.send(embed=embed, view=self)
        
    async def update_item_button(self, sold_item_id, interaction):
        """Update a button in the shop after an item is sold."""
        # Find the index of the sold item in shop_manager.items
        sold_item_index = next((i for i, item in enumerate(shop_manager.items) if item["id"] == sold_item_id), None)
        
        if sold_item_index is not None:
            # Find the button corresponding to the sold item
            button_to_update = next(
                (item for item in self.children 
                 if isinstance(item, ItemButton) and item.item["id"] == sold_item_id), None
            )
            
            if button_to_update:
                # Get the row of the button
                row_number = button_to_update.row
                
                # Get the replacement item from shop_manager
                new_item = shop_manager.items[sold_item_index]
                
                # Remove the old button
                self.remove_item(button_to_update)
                
                # Create a new button with the new item and pass shop_ui reference
                new_button = ItemButton(new_item, context="shop", shop_ui=self)
                new_button.row = row_number
                self.add_item(new_button)
                
                # Create the embed for updating the message
                from database import get_user_data
                user = get_user_data(interaction.user.id)
                
                description = "Browse the available items below."
                if user and "money" in user:
                    description += f"\n\nYour Gold: **{user['money']}**"
                
                embed = discord.Embed(
                    title="Shop",
                    description=description,
                    color=discord.Color.blue()
                )
                
                # Add item categories count
                item_types = {}
                all_items = shop_manager.items + shop_manager.potions
                for item in all_items:
                    item_type = item.get("type", "misc")
                    item_types[item_type] = item_types.get(item_type, 0) + 1
                    
                for item_type, count in item_types.items():
                    embed.add_field(name=f"{item_type.title()}s", value=f"{count} available", inline=True)
                
                # Add note if shop has more items than can be displayed
                if len(all_items) > 25:
                    embed.set_footer(text=f"Showing 25/{len(all_items)} items. Use !shop2 to see more.")
                
                # Update the message with the new view and embed
                await interaction.message.edit(embed=embed, view=self)