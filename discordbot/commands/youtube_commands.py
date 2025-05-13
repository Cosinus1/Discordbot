import discord
from discord.ext import commands
import os
import sys
import asyncio
import tempfile

# Add the youtubedownloader directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'YoutubeDownloader'))

# Import the YouTubeDownloaderBot class
from youtube_downloader_bot import YouTubeDownloaderBot

@commands.command()
async def mp3(ctx, url: str = None):
    """Download a YouTube video as MP3 and send it to the channel."""
    if not url:
        await ctx.send("Please provide a YouTube URL.")
        return
    
    await ctx.send(f"⏳ Downloading MP3 audio from: {url}")
    
    # Create a temporary directory for the download
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize the downloader
        downloader = YouTubeDownloaderBot(save_directory=temp_dir, format_type="MP3")
        
        # Start a typing indicator to show the bot is working
        async with ctx.typing():
            # Download the file
            success, file_path = downloader.download(url)
            
            if not success:
                await ctx.reply(f"❌ Failed to download: {file_path}")
                return
            
            # Check if file exists and its size
            if not os.path.exists(file_path):
                await ctx.reply("❌ Download failed: File not found")
                return
            
            file_size = os.path.getsize(file_path)
            # Discord has an 8MB file size limit for regular users (25MB for Nitro)
            if file_size > 8 * 1024 * 1024:  # 8MB in bytes
                await ctx.reply(f"❌ File size is too large ({file_size / (1024 * 1024):.2f} MB). Discord has an 8MB upload limit.")
                return
            
            # Send the file
            try:
                await ctx.reply(f"✅ Download complete!", file=discord.File(file_path))
            except Exception as e:
                await ctx.reply(f"❌ Error sending file: {str(e)}")

@commands.command()
async def mp4(ctx, url: str = None):
    """Download a YouTube video as MP4 and send it to the channel."""
    if not url:
        await ctx.send("Please provide a YouTube URL.")
        return
    
    await ctx.send(f"⏳ Downloading MP4 video from: {url}")
    
    # Create a temporary directory for the download
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize the downloader
        downloader = YouTubeDownloaderBot(save_directory=temp_dir, format_type="MP4")
        
        # Start a typing indicator to show the bot is working
        async with ctx.typing():
            # Download the file
            success, file_path = downloader.download(url)
            
            if not success:
                await ctx.reply(f"❌ Failed to download: {file_path}")
                return
            
            # Check if file exists and its size
            if not os.path.exists(file_path):
                await ctx.reply("❌ Download failed: File not found")
                return
            
            file_size = os.path.getsize(file_path)
            # Discord has an 8MB file size limit for regular users (25MB for Nitro)
            if file_size > 8 * 1024 * 1024:  # 8MB in bytes
                await ctx.reply(f"❌ File size is too large ({file_size / (1024 * 1024):.2f} MB). Discord has an 8MB upload limit.")
                return
            
            # Send the file
            try:
                await ctx.reply(f"✅ Download complete!", file=discord.File(file_path))
            except Exception as e:
                await ctx.reply(f"❌ Error sending file: {str(e)}")