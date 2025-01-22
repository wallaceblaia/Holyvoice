{recentVideos.map((video) => (
  <Card 
    key={video.id} 
    className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
    onClick={() => setSelectedVideo(video)}
  >
    <div className="relative group">
      <div 
        className="h-48 w-full bg-cover bg-center"
        style={{ backgroundImage: `url(https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg)` }}
      />
      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
        <Youtube className="text-white opacity-0 group-hover:opacity-100 transition-opacity h-12 w-12" />
      </div>
    </div>
    <CardHeader>
      <CardTitle className="line-clamp-2 text-base">{video.title}</CardTitle>
      <CardDescription className="flex items-center">
        <Calendar className="mr-1 h-4 w-4" />
        {format(new Date(video.published_at), "d 'de' MMMM 'de' yyyy", { locale: ptBR })}
        {video.is_live && (
          <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
            AO VIVO
          </span>
        )}
      </CardDescription>
    </CardHeader>
  </Card>
))} 