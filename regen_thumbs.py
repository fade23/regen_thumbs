#!/usr/bin/env python

#
# regen_thumbs.py
#
# Copyright (C) Ross Glass 2012 <fade@entropism.org>
# 
# regen_thumbs.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# regen_thumbs.py is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Prerequisites: Python with MySQLdb and crcmod componentsinstalled
#
# Create one or more configuration files in the following format
#
# [database]
# xbmc_db_host: ark
# xbmc_db_user: xbmc
# xbmc_db_passwd: xbmc
# xbmc_db_db: xbmc_video60

# [paths]
# base: /mnt/tank/Media/video			#base path to videos
# sets: /home/rglass/tank/htpc/Sets		#path to movieset posters
# vfs: smb://TANK/Media/video 			#xbmc virtual path to videos

# [movies]
# path: /movies/features				#path to feature films, relative to base
# poster: poster.jpg					#file pattern for movie posters
# fanart: fanart.jpg					#file pattern for movie fanart

# [series]
# path: /series							#path to series, relative to base
# poster: poster.jpg					#file pattern for series posters
# banner: banner.jpg					#file pattern for series banners
# fanart: fanart.jpg					#file pattern for series fanart
# default: poster						#indicates default format to use for xbmc thumbs, poster or banner

# [targets]
# targets[1]: /home/rglass/tank/htpc/XBMC/userdata/Thumbnails/Video		#destination for new thumbnails

# [types]
# movies: 0								#generate movie thumbnails, set to 1 to enable
# sets: 1								#generate movieset thumbnails, set to 1 to enable
# series: 0								#generate series thumbnails, set to 1 to enable
# seasons: 0							#generate seasons thumbnails, set to 1 to enable
# episodes: 0							#generate episode thumbnails, set to 1 to enable


from crcmod import mkCrcFun
import os,shutil,string,sys, MySQLdb
import ConfigParser

g=mkCrcFun(0x104C11DB7,rev=False)

def getCrc(filename):
    crc     = hex(g(filename.lower()))
    nicecrc = str(crc[2:-1]).lower()
    return str(nicecrc).zfill(8)

def makeThumbsMovies():

	for dir in os.listdir(dirMovies):
		dir2 = dirMovies + '/' + dir
		for file in os.listdir(dir2):
			size = os.path.getsize(dir2 + '/' + file)
			strName = file[:-4]
			
			#Check the file size and that it's not a trailer
			if size > 100000000 and file[-12:-4] <> '-trailer':
				vfsLocation = dir2.replace(dirBase,vfsBase) + '/' + file
				crc= getCrc(vfsLocation)
				
				#look for the poster and copy it as the primary thumbnail
				poster = dir2 + '/' + posterMovies
				folder = dir2 + '/' + 'folder.jpg'
				
				#if no poster exists, copy it from folder
				
				if os.path.exists(poster):
					#copy the poster to the folder
					print poster + ' >> ' + folder
					shutil.copy(poster,folder)
					
				else:
					#if no poster, fall back to use the folder
					if os.path.exists(folder):
						print folder + ' >> ' + poster
						shutil.copy(folder,poster)
				
				for x,y in targets.iteritems():

					dirThumbnails = y
					
					posterthumb = dirThumbnails + '/' + crc[0] + '/' + crc + '.tbn'
					posterdds = dirThumbnails + '/' + crc[0] + '/' + crc + '.dds'
					
					if os.path.exists(poster):
						print poster + ' >> ' + posterthumb
						shutil.copy(poster,posterthumb)
						
						#remove the dds so xbmc will regenerate it
						if os.path.exists(posterdds):
							os.remove(posterdds)
					
					#look for the fanart and copy it as the fanart thumbnail	
					fanart = dir2 + '/' + fanartMovies
					fanartthumb = dirThumbnails + '/Fanart/' + crc + '.tbn'
					fanartdds = dirThumbnails + '/Fanart/' + crc + '.dds'
					if os.path.exists(fanart):
						print fanart + ' >> ' + fanartthumb
						shutil.copy(fanart,fanartthumb)
						
						#remove the dds so xbmc will regenerate it
						if os.path.exists(fanartdds):
							os.remove(fanartdds)				

def makeThumbsSets():

	global xbmc_db_host
	global xbmc_db_user
	global xbmc_db_passwd
	global xbmc_db_db

	conn = MySQLdb.connect (host = xbmc_db_host,
                           user = xbmc_db_user,
                           passwd = xbmc_db_passwd,
                           db = xbmc_db_db)
	cursor = conn.cursor ()
	
	for file in os.listdir(dirSets):

		poster = dirSets + '/' + file
		
		strName = file[:-4]
		strSQL = 'SELECT idSet FROM sets WHERE strSet = "' + strName + '"'

		cursor.execute (strSQL)
		row = cursor.fetchone ()
		
		idSet = str(row[0])
		HashSet = 'videodb://1/7/' + idSet + '/'
		crc = getCrc(HashSet)
							
		for x,y in targets.iteritems():

			dirThumbnails = y
			
			posterthumb = dirThumbnails + '/' + crc[0] + '/' + crc + '.tbn'
			posterdds = dirThumbnails + '/' + crc[0] + '/' + crc + '.dds'
			
			if os.path.exists(poster):
				print poster + ' >> ' + posterthumb
				shutil.copy(poster,posterthumb)
				
				#remove the dds so xbmc will regenerate it
				if os.path.exists(posterdds):
					os.remove(posterdds)							
					
def makeThumbsSeries():

	for dir in os.listdir(dirSeries):
		vfsLocation = dirSeries.replace(dirBase,vfsBase) + '/' + dir + '/'
		crc= getCrc(vfsLocation)

		#look for the poster or banner and copy it as the primary thumbnail

		if defaultSeries == 'poster':
			default = dirSeries + '/' + dir + '/' + posterSeries
		else:	
			default = dirSeries + '/' + dir + '/' + bannerSeries
			
		folder = dirSeries + '/' + dir + '/' + 'folder.jpg'
		
		for x,y in targets.iteritems():

			dirThumbnails = y		
		
			defaultthumb = dirThumbnails + '/' + crc[0] + '/' + crc + '.tbn'
			defaultdds = dirThumbnails + '/' + crc[0] + '/' + crc + '.dds'		
			
			if os.path.exists(default):
				print default + '>> ' + defaultthumb
				shutil.copy(default,defaultthumb)
				# copy the default to the folder
				shutil.copy(default,folder)
				
			# look for the fanart and copy it as the fanart thumbnail	
			fanart = dirSeries + '/' + dir + '/' + fanartSeries
			fanartthumb = dirThumbnails + '/Fanart/' + crc + '.tbn'
			fanartdds = dirThumbnails + '/Fanart/' + crc + '.dds'
			if os.path.exists(fanart):
				print fanart + ' >> ' + fanartthumb
				shutil.copy(fanart,fanartthumb)
				
				# remove the dds so xbmc will regenerate it
				if os.path.exists(fanartdds):
					os.remove(fanartdds)	

def makeThumbsSeasons():
	for dir in os.listdir(dirSeries):
		vfsLocation = dirSeries.replace(dirBase,vfsBase) + '/' + dir + '/'
				
		#look for season thumbs
		dir2 = dirSeries + '/' + dir
		for file in os.listdir(dir2):

			if file[:6] == 'season' and file[-4:] == '.tbn':
				strSeason = file[6:-4]
										
				if strSeason[0] == '0' or strSeason[0] == '-':
					strSeason = strSeason[1:]
				
				if strSeason == 'specials':
					hashSeason = 'season' + vfsLocation + 'Season Specials'
					
				elif strSeason == 'all':
					hashSeason = 'season' + vfsLocation + 'Season All'
				
				else:		
					hashSeason = 'season' + vfsLocation + 'Season ' + strSeason
					
					
				crc = getCrc(hashSeason	)
				
				season = dir2 + '/' + file
				
				for x,y in targets.iteritems():

					dirThumbnails = y					
				
					seasonthumb = dirThumbnails + '/' + crc[0] + '/' + crc + '.tbn'
					seasondds = dirThumbnails + '/' + crc[0] + '/' + crc + '.dds'
					
					print season + ' >> ' + seasonthumb
					shutil.copy(season,seasonthumb)
					
					#remove the dds so xbmc will regenerate it
					if os.path.exists(seasondds):
						os.remove(seasondds)
						
def makeThumbsEpisodes():
		for dir in os.listdir(dirSeries):
				
			#look for season dirs
			dir2 = dirSeries + '/' + dir
			
			for dir3 in os.listdir(dir2):	
				
				if dir3[:6] == 'Season':
				
					dir3 = dir2 + '/' + dir3
					
					if os.path.isdir(dir3):
					
						for file in os.listdir(dir3):
							size = os.path.getsize(dir3 + '/' + file)
							
							if size > 10000000:
							
								vfsLocation = dir3.replace(dirBase,vfsBase) + '/' + file
								crc= getCrc(vfsLocation)
								
								episode = dir3 + '/' + file[:-4] + '.tbn'
								
								if os.path.isfile(episode):
								
									for x,y in targets.iteritems():

										dirThumbnails = y
								
										episodethumb = dirThumbnails + '/' + crc[0] + '/' + crc + '.tbn'
										episodedds = dirThumbnails + '/' + crc[0] + '/' + crc + '.dds'
										
										print episode + ' >> ' + episodethumb
										
										shutil.copy(episode,episodethumb)
						
										#remove the dds so xbmc will regenerate it
										if os.path.exists(episodedds):
											os.remove(episodedds)

#get the config values	
config_file = sys.argv[1]
config = ConfigParser.RawConfigParser()
config.read(config_file)

xbmc_db_host = config.get('database', 'xbmc_db_host')
xbmc_db_user = config.get('database', 'xbmc_db_user')
xbmc_db_passwd = config.get('database', 'xbmc_db_passwd')
xbmc_db_db = config.get('database', 'xbmc_db_db')

#path to videos
dirBase = config.get('paths', 'base')

#xbmc vfs path to videos
vfsBase = config.get('paths', 'vfs')

#directory with the set thumbnails
dirSets = config.get('paths', 'sets')

#subdiretory of movies
dirMovies=dirBase + config.get('movies', 'path')

#pattern for movie poster
posterMovies = config.get('movies', 'poster')

#pattern for movie fanart
fanartMovies = config.get('movies', 'fanart')

#subdirectories of series
dirSeries=dirBase + config.get('series', 'path')

#pattern for series poster
posterSeries = config.get('series', 'poster')

#pattern for series banner
bannerSeries = config.get('series', 'banner')

#pattern for series fanart
fanartSeries = config.get('series', 'fanart')

#use poster or banner for the default series thumbnail
defaultSeries = config.get('series', 'default')

#array of target thumbnail directories
targets = {}
targets[1] = config.get("targets", "targets[1]")
											
#makeThumbsMovies()		
makeThumbsSets()
#makeThumbsSeries()
#makeThumbsSeasons()							
#makeThumbsEpisodes()
