#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode

from django.db.models import Q

import json
import parser
import my_utils


from controller.notificationcontroller import *

from pyofc2  import * 
import random
import time

from datetime import datetime
import datetime as dt
from django.db.models import Q

from django.db.models import Count

import random

from tempfile import TemporaryFile
from xlwt import Workbook, easyxf, Formula,Utils

from controller.admincontroller import *

def process_test(request):
    start_date=request.GET.get('start','')
    end_date=request.GET.get('end','')
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    if start_date == '':
        start_date=this_week_start.strftime("%Y-%m-%d")
    if end_date == '':
        end_date=this_week_end.strftime("%Y-%m-%d")
    
    start_date=time.strptime(start_date,'%Y-%m-%d')
    start_date=dt.datetime.fromtimestamp(time.mktime(start_date))
    end_date=time.strptime(end_date,'%Y-%m-%d')
    end_date=dt.datetime.fromtimestamp(time.mktime(end_date))
    end_date=end_date+dt.timedelta(1)
    
    wb = Workbook()
    ws = wb.add_sheet('Sheetname')
    ws.write(0, 0, 'Firstname')
    ws.write(0, 1, 'Surname')
    ws.write(1, 0, 'Hans')
    ws.write(1, 1, 'Muster')

    fname = 'process_excel-testfile.xls'
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    wb.save(response)

    return response
    
    
def process(request):
    print request.POST
    
    wb = Workbook(encoding='utf-8')
    
    overview = request.POST.get('overview',False)
    each_topic = request.POST.get('each_topic',False)
    each_topic_total = request.POST.get('each_topic_total',False)
    each_user = request.POST.get('each_user',False)
    each_user_total = request.POST.get('each_user_total',False)
    each_day = request.POST.get('each_day',False)
    most_replied = request.POST.get('most_replied',False)
    message_list = request.POST.get('message_list',False)
    
    start_date_str = request.POST.get('start_date','')
    end_date_str = request.POST.get('end_date','')
    
    start_date=time.strptime(start_date_str,'%Y-%m-%d')
    start_date=dt.datetime.fromtimestamp(time.mktime(start_date))
    end_date=time.strptime(end_date_str,'%Y-%m-%d')
    end_date=dt.datetime.fromtimestamp(time.mktime(end_date)) + dt.timedelta(1) - dt.timedelta(seconds=1)
    
    if overview:
        prepare_overview(wb,start_date,end_date)
        
    if each_topic:    
        prepare_each_topic(wb,start_date,end_date)
    if each_topic_total:
        prepare_each_topic_total(wb,start_date,end_date)
    
    if each_user:    
        prepare_each_user(wb,start_date,end_date)
    if each_user_total:
        prepare_each_user_total(wb,start_date,end_date)
        
    if each_day:
        prepare_each_day(wb,start_date,end_date)

    if most_replied:
        prepare_most_replied(wb,start_date,end_date)
        
    if message_list:
        prepare_message_list(wb,start_date,end_date)        

    fname = 'Cloud31_Data_'+start_date_str+'_'+end_date_str+'.xls'
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    
    
    sheet = wb.add_sheet('Sheet')
    wb.save(response)
    
    
    return response

font_style=easyxf('font: bold False, height 220;')

def prepare_most_replied(wb,start_date,end_date):
    sheet = wb.add_sheet('최다 댓글 메세지(기간 내)')
    
    sheet.write(0,0,'시작',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(0,1,str(start_date))
    sheet.write(1,0,'종료',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(1,1,str(end_date))
    
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'border: bottom thin;' 'pattern: pattern solid, fore_color light_green;')
    
    messages = Comment.objects.filter(is_deleted=False,reg_date__range=(start_date,end_date), message__is_deleted=False).values('message').annotate(count = Count('message')).order_by('-count')
    
    row=2
    col=0
    
    sheet.write(row+2,0,'최다 댓글 메시지 리스트',easyxf('font: bold True, height 220;'))
    sheet.col(3).width=10000
    sheet.col(4).width=5000
    sheet.col(6).width=4000
    sheet.col(7).width=4000
    sheet.col(8).width=4000
    
    for message in messages:
        row+=3
        col=0
        feed_id = message['message']
        try:
            sheet.write(row,0,'id',header_style)
            sheet.write(row,1,'replied_to_id',header_style)
            sheet.write(row,2,'author',header_style)
            sheet.write(row,3,'contents',header_style)
            sheet.write(row,4,'reg_date',header_style)
            sheet.write(row,5,'is_deleted',header_style)
            sheet.write(row,6,'location',header_style)
            sheet.write(row,7,'related_topics',header_style)
            sheet.write(row,8,'related_users',header_style)
            sheet.write(row,9,'attach_files',header_style)
        
            feed= Message.objects.get(id=feed_id)
            row+=1
            sheet.write(row,0,"Message#"+str(feed.id),font_style)
            sheet.write(row,1,'',font_style)
            sheet.write(row,2,feed.author.last_name,font_style)
            sheet.write(row,3,feed.contents,font_style)
            sheet.write(row,4,str(feed.reg_date),font_style)
            sheet.write(row,5,feed.is_deleted,font_style)

            if feed.lat != '' and feed.lng != '':
                sheet.write(row,6,str(feed.lat)+','+str(feed.lng),font_style)
            else:
                sheet.write(row,6,'',font_style)
            sheet.write(row,7,feed.related_topics,font_style)
            sheet.write(row,8,feed.related_users,font_style)
            sheet.write(row,9,feed.attach_files,font_style)
            
            comments = Comment.objects.filter(message=feed,reg_date__range=(start_date,end_date), is_deleted=False)
            for comment in comments:
                row+=1
                sheet.write(row,0,"Comment#"+str(comment.id),font_style)
                sheet.write(row,1,"Message#"+str(feed.id),font_style)
                sheet.write(row,2,comment.author.last_name,font_style)
                sheet.write(row,3,comment.contents,font_style)
                sheet.write(row,4,str(comment.reg_date),font_style)
                sheet.write(row,5,comment.is_deleted,font_style)
        except Exception as e:
            print str(e)
            pass
    

def prepare_message_list(wb,start_date,end_date):
    sheet = wb.add_sheet('메시지 리스트(기간 내)')
    
    sheet.write(0,0,'시작',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(0,1,str(start_date))
    sheet.write(1,0,'종료',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(1,1,str(end_date))
    
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'border: bottom thin;' 'pattern: pattern solid, fore_color light_green;')
    messages = Message.objects.filter(reg_date__range=(start_date,end_date))
    
    from django.forms.models import model_to_dict
    temp_msg = model_to_dict(Message())
    
    sheet.col(2).width=10000
    sheet.col(4).width=5000
    sheet.col(5).width=4000
    sheet.col(6).width=4000
    
    
    row=3
    col=1
    sheet.write(row,0,'id',header_style)
    sheet.write(row,1,'author',header_style)
    for key in sorted(temp_msg.iterkeys()):
        if key in ['author','attach_files','id','lat','write_from']:
            continue
        if key == 'lng':
            col+=1
            sheet.write(row,col,'location',header_style)
            continue
        col+=1
        sheet.write(row,col,key,header_style)
    col+=1
    sheet.write(row,col,'attach_files',header_style)
          
    for message in messages:
        message_dict = model_to_dict(message)
        row+=1
        col=1
        sheet.write(row,0,message.id)
        sheet.write(row,1,message.author.last_name)
        location=''
        for key in sorted(message_dict.iterkeys()):
            if key in ['author','attach_files','id','write_from']:
                continue
            if key == 'lat':
                if message_dict[key] != "":
                    location += message_dict[key] +','
                continue
            if key == 'lng':
                col+=1
                sheet.write(row,col,location+message_dict[key],font_style)
                continue
            col+=1
            sheet.write(row,col,message_dict[key])
        col+=1
        sheet.write(row,col,message.attach_files)


def prepare_each_day(wb,start_date,end_date):
    sheet = wb.add_sheet('일별 Feed 개수(기간 내)')
    sheet.write(0,0,'시작',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(0,1,str(start_date))
    sheet.write(1,0,'종료',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(1,1,str(end_date))
    
    
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'border: bottom thin;' 'pattern: pattern solid, fore_color light_green;')
    header_style2=easyxf( 'font: name Arial, bold True, height 220;' 'border: top thin;' 'pattern: pattern solid, fore_color light_green;')
    header_style3=easyxf( 'font: name Arial, bold True, height 220;' 'pattern: pattern solid, fore_color light_green;')
    sheet.write(3,0,'시간',header_style3)
    sheet.write(3,1,'사용자',header_style3)
    sheet.write(4,0,'날짜',header_style)
    user_profiles = UserProfile.objects.filter(is_deactivated=False)
    
    row=4
    col=0
    for user_profile in user_profiles:
        try:
            user = user_profile.user
            col+=1
            if col != 1:
                sheet.write(row-1,col,'',header_style3)
            sheet.write(row,col,user.last_name,header_style)
        except Exception as e:
            print str(e)
            pass
    
    col+=1
    sheet.write(row-1,col,'',header_style3)
    sheet.write(row,col,'합계',header_style)
    
    
    time = start_date
    
    row=4
    col=0
    while time < end_date:
        next_time = time + dt.timedelta(1) - dt.timedelta(seconds=1)
        col=0
        row+=1
        sheet.write(row,col,time.strftime('%Y.%m.%d'),easyxf('font: bold False, height 220;', num_format_str='YYYY.MM.DD'))
        row_total=0
        for user_profile in user_profiles:
            try:
                user = user_profile.user
                col+=1
                count = Message.objects.filter(is_deleted=False, reg_date__range=(time,next_time), author=user).count()
                row_total+=count
                if count != 0:
                    sheet.write(row,col,count,font_style)
            except Exception as e:
                print str(e)
                pass
        col+=1
        start = Utils.rowcol_to_cell(row,1)
        end = Utils.rowcol_to_cell(row,col-1)
        sheet.write(row,col,Formula("SUM("+start+":"+end+")"),font_style)
        time = time + dt.timedelta(1)
    
    row+=1
    col=0
    sheet.write(row,col,'합계',header_style2)
    for user_profile in user_profiles:
        try:
            col+=1
            start = Utils.rowcol_to_cell(5,col)
            end = Utils.rowcol_to_cell(row-1,col)
            count = Formula("SUM("+start+":"+end+")")
            sheet.write(row,col,count,header_style2)
        except Exception as e:
            print str(e)
            pass
    col+=1
    start = Utils.rowcol_to_cell(5,col)
    end = Utils.rowcol_to_cell(row-1,col)
    count = Formula("SUM("+start+":"+end+")")
    sheet.write(row,col,count,header_style2)
    
def prepare_each_user(wb,start_date,end_date):
    sheet = wb.add_sheet('사용자별 Feed 개수(기간 내)')
    sheet.write(0,0,'시작',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(0,1,str(start_date))
    sheet.write(1,0,'종료',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(1,1,str(end_date))
    
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'border: bottom thin;' 'pattern: pattern solid, fore_color light_green;')
    header_style2=easyxf( 'font: name Arial, bold True, height 220;' 'border: top thin;' 'pattern: pattern solid, fore_color light_green;')
    
    sheet.write(3,0,'사용자',header_style)   
    sheet.write(3,1,'작성 Feed 수',header_style)
    sheet.write(3,2,'작성 댓글 수',header_style)
    sheet.write(3,3,'첨부 파일 수',header_style)
    
    row=3
    
    feed_total=0
    comment_total=0
    file_total=0
    user_profiles = UserProfile.objects.filter(is_deactivated=False)
    for user_profile in user_profiles:
        try:
            user = user_profile.user
            messages = Message.objects.filter(is_deleted=False, reg_date__range=(start_date,end_date), author=user)
            comments = Comment.objects.filter(is_deleted=False, reg_date__range=(start_date,end_date), author=user)
            row+=1
            sheet.write(row,0,user.last_name,font_style)
            sheet.write(row,1,len(messages),font_style)
            sheet.write(row,2,len(comments),font_style)
            
            attach_count=0
            for message in messages:
                arr=message.attach_files.split(',')
                for item in arr:
                    if item != '':
                        attach_count+=1
            sheet.write(row,3,attach_count,font_style)
            feed_total+=len(messages)
            comment_total+=len(comments)
            file_total+=attach_count
        except Exception as e:
            print str(e)
            pass
    
    row+=1
    sheet.write(row,0,'총',header_style2)
    sheet.write(row,1,feed_total,header_style2)
    sheet.write(row,2,comment_total,header_style2)
    sheet.write(row,3,file_total,header_style2)


def prepare_each_user_total(wb,start_date,end_date):
    sheet = wb.add_sheet('사용자별 Feed 개수(전체)')
    
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'border: bottom thin;' 'pattern: pattern solid, fore_color light_green;')
    header_style2=easyxf( 'font: name Arial, bold True, height 220;' 'border: top thin;' 'pattern: pattern solid, fore_color light_green;')
    sheet.write(1,0,'사용자',header_style)   
    sheet.write(1,1,'작성 Feed 수',header_style)
    sheet.write(1,2,'작성 댓글 수',header_style)
    sheet.write(1,3,'첨부 파일 수',header_style)
    
    row=1
    
    feed_total=0
    comment_total=0
    file_total=0
    user_profiles = UserProfile.objects.filter(is_deactivated=False)
    for user_profile in user_profiles:
        try:
            user = user_profile.user
            messages = Message.objects.filter(is_deleted=False, author=user)
            comments = Comment.objects.filter(is_deleted=False, author=user)
            row+=1
            sheet.write(row,0,user.last_name,font_style)
            sheet.write(row,1,len(messages),font_style)
            sheet.write(row,2,len(comments),font_style)
            
            attach_count=0
            for message in messages:
                arr=message.attach_files.split(',')
                for item in arr:
                    if item != '':
                        attach_count+=1
            sheet.write(row,3,attach_count,font_style)
            feed_total+=len(messages)
            comment_total+=len(comments)
            file_total+=attach_count
        except Exception as e:
            print str(e)
            pass
    
    row+=1
    sheet.write(row,0,'총',header_style2)
    sheet.write(row,1,feed_total,header_style2)
    sheet.write(row,2,comment_total,header_style2)
    sheet.write(row,3,file_total,header_style2)

def prepare_each_topic_total(wb,start_date,end_date):
    sheet = wb.add_sheet('Topic별 Feed 개수(전체)')

    #기간 내 신규 토픽
    sheet.write(0,0,'전체 토픽 수',easyxf('font:bold True, height 220;'))
    sheet.col(0).width = 6000
    topic_length = Topic.objects.filter(topic_name__gt="").count()
    sheet.write(0,1,topic_length)
    
    #토픽 별 메시지 수
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'pattern: pattern solid, fore_color light_green;')
    sheet.write(2,0,'토픽',header_style)
    sheet.write(2,1,'개수',header_style)
    
    topics = Topic.objects.filter(topic_name__gt="")
    row=2
    total = 0
    for topic in topics:
        try:
            reference_count = Message.objects.filter(is_deleted=False,related_topics__contains=topic.topic_name).count()
            total+=reference_count
            row+=1
            sheet.write(row,0,topic.topic_name)
            sheet.write(row,1,reference_count)
        except Exception as e:
            print str(e)
            pass
    
    row+=1
    sheet.write(row,0,'총 합계',header_style)
    sheet.write(row,1,total,header_style)
    
    sheet.write(1,3,'Most popular topic의 메시지')
    row=2
    sheet.write(row,3,'토픽',header_style)
    sheet.write(row,4,'작성자',header_style)
    sheet.write(row,5,'내용',header_style)
    sheet.write(row,6,'작성일',header_style)
    
    sheet.col(4).width = 5000
    sheet.col(5).width = 10000
    sheet.col(6).width = 5000
    pop_topics = TopicTimeline.objects.filter(message__is_deleted=False, topic__topic_name__gt='').values('topic').annotate(topic_count=Count('topic')).order_by("-topic_count")[:5]
    
    for item in pop_topics:
        try:
            topic = Topic.objects.get(id=item['topic'])
            topic_timelines = TopicTimeline.objects.filter(message__is_deleted=False, topic=topic)
            for timeline in topic_timelines:
                row+=1
                sheet.write(row,3,topic.topic_name,font_style)
                sheet.write(row,4,timeline.message.author.last_name+'('+timeline.message.author.username+')',font_style)
                sheet.write(row,5,timeline.message.contents,font_style)
                sheet.write(row,6,str(timeline.message.reg_date),font_style)                
        except Exception as e:
            print str(e)
            pass
    
def prepare_each_topic(wb,start_date,end_date):
    sheet = wb.add_sheet('Topic별 Feed 개수(기간 내)')
    
    sheet.write(0,3,'시작일',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(0,4,str(start_date))
    sheet.write(1,3,'종료일',easyxf('font: bold True, height 220;' 'alignment: horizontal center;'))
    sheet.write(1,4,str(end_date))
    #전체 토픽 수
    sheet.write(0,0,'전체 토픽 수',easyxf('font:bold True, height 220;'))
    sheet.col(0).width = 6000
    topic_length = Topic.objects.filter(topic_name__gt="").count()
    sheet.write(0,1,topic_length)
    
    #토픽 별 메시지 수
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'pattern: pattern solid, fore_color light_green;')
    sheet.write(2,0,'토픽',header_style)
    sheet.write(2,1,'개수',header_style)
    
    topics = Topic.objects.filter(topic_name__gt="")
    row=2
    total = 0
    for topic in topics:
        try:
            reference_count = Message.objects.filter(reg_date__range=(start_date,end_date),is_deleted=False,related_topics__contains=topic.topic_name).count()
            total+=reference_count
            row+=1
            sheet.write(row,0,topic.topic_name,font_style)
            sheet.write(row,1,reference_count,font_style)
        except Exception as e:
            print str(e)
            pass
    
    row+=1
    sheet.write(row,0,'총 합계',header_style)
    sheet.write(row,1,total,header_style)
    
    #기간 내 신규 토픽
    sheet.col(3).width = 6000
    this_week_topics = Topic.objects.filter(reg_date__range=(start_date,end_date), topic_name__gt="")
    sheet.write(2,3,'기간 내 신규 토픽 ('+str(len(this_week_topics))+'개)',header_style)
    new_row=3
    for topic in this_week_topics:
        new_row+=1
        sheet.write(new_row,3,topic.topic_name)
    
    row=new_row+4
    sheet.write(row-1,3,'Most popular topic의 메시지',font_style)
    sheet.write(row,3,'토픽',header_style)
    sheet.write(row,4,'작성자',header_style)
    sheet.write(row,5,'내용',header_style)
    sheet.write(row,6,'작성일',header_style)
    
    sheet.col(4).width = 5000
    sheet.col(5).width = 10000
    sheet.col(6).width = 5000
    pop_topics = TopicTimeline.objects.filter(message__is_deleted=False,message__reg_date__range=(start_date,end_date), topic__topic_name__gt='').values('topic').annotate(topic_count=Count('topic')).order_by("-topic_count")[:5]
    
    for item in pop_topics:
        try:
            topic = Topic.objects.get(id=item['topic'])
            topic_timelines = TopicTimeline.objects.filter(message__is_deleted=False,message__reg_date__range=(start_date,end_date), topic=topic)
            for timeline in topic_timelines:
                row+=1
                sheet.write(row,3,topic.topic_name,font_style)
                sheet.write(row,4,timeline.message.author.last_name+'('+timeline.message.author.username+')',font_style)
                sheet.write(row,5,timeline.message.contents,font_style)
                sheet.write(row,6,str(timeline.message.reg_date),font_style)                
        except Exception as e:
            print str(e)
            pass
    
    
    
def prepare_overview(wb,start_date,end_date):
    sheet1 = wb.add_sheet('전체 통계')
    sheet1.col(1).width = 5000
    header_style=easyxf( 'font: name Arial, bold True, height 220;' 'alignment: horizontal center;' 'borders: left medium, right medium, top medium, bottom medium;' \
                    'pattern: pattern solid, fore_color light_green;')
    sheet1.write(1,1,'항목',header_style)
    sheet1.write(1,2,'개수',header_style)
    
    item_style1=easyxf( 'font: name Arial, height 220;' 'alignment: horizontal center;' 'borders: left medium, right thin;')
    
    item_style2=easyxf( 'font: name Arial, height 220;' 'alignment: horizontal center;' 'borders: left thin, right medium;')
    item_style3=easyxf( 'font: name Arial, height 220;' 'alignment: horizontal center;' 'borders: left medium, right thin, bottom medium;')
    
    item_style4=easyxf( 'font: name Arial, height 220;' 'alignment: horizontal center;' 'borders: left thin, right medium, bottom medium;')
    
    
    sheet1.write(2,1,'전체 메시지 개수',item_style1)
    feed_length = Message.objects.filter(is_deleted=False).count()
    sheet1.write(2,2,feed_length,item_style2)
    
    sheet1.write(3,1,'전체 Topic 개수',item_style1)
    topic_length = Topic.objects.filter(topic_name__gt="").count()
    sheet1.write(3,2,topic_length,item_style2)
    
    sheet1.write(4,1,'오늘 Feed 개수',item_style1)
    now = datetime.now()
    year,month,day = now.year, now.month, now.day
    today_start = dt.date(year, month, day)
    today_end = dt.date(year, month, day)  + dt.timedelta(1)
    feed_today_length = Message.objects.filter(is_deleted=False, reg_date__range=(today_start,today_end)).count()  
    sheet1.write(4,2,feed_today_length,item_style2)
    
    
    sheet1.write(5,1,'현재 멤버수',item_style1)
    user_length = UserProfile.objects.filter(is_deactivated=False).count()
    sheet1.write(5,2,user_length,item_style2)
    
    
    file_total_length = File.objects.filter(is_attached=True).count()
    
    image_type_list = ['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF']
    image_total_length = File.objects.filter(is_attached=True, file_type__in=image_type_list).count()
    sheet1.write(6,1,'첨부 파일 수',item_style1)
    sheet1.write(6,2,file_total_length-image_total_length,item_style2)
    
    sheet1.write(7,1,'첨부 사진 수',item_style1)
    sheet1.write(7,2,image_total_length,item_style2)
    
    
    location_length = Message.objects.filter(is_deleted=False, lat__gt="", lng__gt="").count()
    sheet1.write(8,1,'첨부 위치 수',item_style3)
    sheet1.write(8,2,location_length,item_style4)
    
 