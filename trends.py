from googleapiclient.discovery import build
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob




API_KEY='your youtube API KEY'
YOUTUBE_API_SERVICE_NAME='youtube'
YOUTUBE_API_VERSION='v3'

youtube=build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=API_KEY)

request=youtube.videos().list(
part='snippet,statistics',
    chart='mostPopular',
    regionCode='LK',
    maxResults=50
)

response=request.execute()

videos=[]

for item in response['items']:
    video = {
        'title': item['snippet']['title'],
        'comments': int(item['statistics'].get('commentCount', 0)),
        'category': item['snippet']['categoryId'],
        'views': int(item['statistics']['viewCount']),
        'likes': int(item['statistics'].get('likeCount', 0)),
        'dislikes': int(item['statistics'].get('dislikeCount', 0)),
        'channel': item['snippet']['channelTitle'],
    }
    videos.append(video)

df=pd.DataFrame(videos)
print(df.head(100))

# Most popular categories
category_counts = df['category'].value_counts()
plt.figure(figsize=(10, 6))
sns.barplot(x=category_counts.index, y=category_counts.values)
plt.title('Most Popular Categories')
plt.xlabel('Category ID')
plt.ylabel('Number of Videos')
plt.xticks(rotation=45)  
plt.show()

# Correlation between views, likes, and comments
plt.figure(figsize=(8, 6))
sns.heatmap(df[['views', 'likes', 'comments']].corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

# Top 10 most viewed videos
top_10_videos = df.nlargest(10, 'views')[['title', 'views']]
print(top_10_videos)

# Combine all titles into a single string
titles_text = ' '.join(df['title'])

# Generate word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(titles_text)

# Plot word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Trending Video Titles')
plt.show()


df['sentiment']=df['title'].apply(lambda x:TextBlob(x).sentiment.polarity)
print(df[['title', 'sentiment']].head())

trending_channels = df['channel'].value_counts().head(10)
print(trending_channels)

df['engagement_rate'] = (df['likes'] + df['comments']) / df['views']
print(df[['title', 'engagement_rate']].sort_values(by='engagement_rate', ascending=False).head())

df.to_csv('youtube_trending_data.csv', index=False)
