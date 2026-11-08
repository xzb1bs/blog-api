from django.contrib import admin, messages
from django.db import models
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display 
from unfold.enums import ActionVariant
from unfold.sections import TableSection


from apps.blog.models import Category, Comment, Post, Tag


comment_preview_length = 60
comments_per_page = 10
post_list_url_name = "admin:blog_post_changelist"



class CategoryPostsSection(TableSection):
    verbose_name = "Posts"
    height = 300
    related_name = "posts"
    fields = ["title", "status", "created_at"]

class PostCommentsSection(TableSection):
    verbose_name = "Comments"
    height = 300
    related_name = "comments"
    fields = ["author", "body", "created_at"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(posts_total=Count("posts"))

    @display(description="Posts", ordering = "posts_total")
    def posts_count(self, obj):
        return obj.posts_total


@admin.register(Tag)
class TagAdmin(ModelAdmin):
        list_display = ("name", "slug", "posts_count")
        search_fields = ("name",)
        prepopulated_fields = {"slug": ("name",)}

        def get_queryset(self, request):
            return super().get_queryset(request).annotate(posts_total=Count("posts")) 

        @display(description="Posts", ordering = "posts_total")
        def posts_count(self, obj):
            return obj.posts_total

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
     list_display = ("post_title", "author", "body_preview", "created_at")
     list_filter = [
          ("post", AutocompleteSelectFilter),
          ("author", AutocompleteSelectFilter),
          ("created_at", AutocompleteSelectFilter),
     ]
     list_filter_submit = True
     search_fields = ("body", "author__email", "post__title")
     autocomplete_fields = ("post", "author")
     list_select_related = ("post", "author")

     @display(description="Posts", ordering = "posts_total")
     def posts_count(self, obj):
        return obj.posts_total

     @display(description="Post", ordering="post__title")
     def post_title(self, obj):
        return obj.post.title

     @display(description = "Comment")
     def body_preview(self, obj):
        if len(obj.body) <= comment_preview_length:
            return obj.body
        return obj.body[:comment_preview_length] + "..."



class CommentInLine(TabularInline):
    model = Comment
    tab = True
    per_page = comments_per_page
    extra = 0
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("post_header", "status_label", "category", "tags_dropdown", "comments_count", "created_at")
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ("title", "body", "author__email")
    list_selected_related = ("author", "category")
    list_sections = [PostCommentsSection]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category", "tags")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CommentInLine]
    warn_unsaved_form = True
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}

    fieldsets = (
        ("Content", {"classes": ["tab"], "fields": ("title", "slug", "body")}),
        ("Classification", {"classes": ["tab"], "fields": ("category", "tags", "status")}),
        ("Meta", {"classes": ["tab"], "fields": ("author", "created_at", "updated_at")}),
    ) 
    actions = ["publish_selected", "move_to_drafts"]
    actions_row = ["toggle_publish"]
    actions_list = ["publish_all_drafts"]
    actions_detail = ["open_comments"]
    actions_submit_line = ["save_and_publish"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(comments_total=Count("comments", distinct=True)).prefetch_related("tags")

    @display(description = "Post", header=True)
    def post_header(self, obj):
        author = f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return [obj.title, author]

    @display(description="Status", ordering="status", label={"published": "success", "draft": "warning"})
    def status_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(description ="Tags", dropdown = True)
    def tags_dropdown(self,obj):
        tags = obj.tags.all()
        items = []
        for tag in tags:
            items.append({"title": tag.name, "link": reverse("admin:blog_tag_change", args=[tag.pk])})
        return{"title": f"{len(tags)} tags", "items": items}
    @display(description="Comments", ordering="comments_total")
    def comments_count(self, obj):
        return obj.comments_total

    @action(description="Publish selected")
    def publish_selected(self, request, queryset):
        updated = queryset.update(status=Post.Status.PUBLISHED, updated_at=timezone.now())
        self.message_user(request, f"published posts: {updated}", messages.SUCCESS)

    @action(description="publish / unpublish")
    def toggle_publish(self, request, object_id):
        post = get_object_or_404(Post, pk=object_id)
        if post.status == Post.Status.PUBLISHED:
             post.status = Post.Status.DRAFT
        else:
            post.status = Post.Status.PUBLISHED
        post.save()
        self.message_user(request, f"'{post.title}' is now {post.get_status_display().lower()}")
        return redirect(reverse(post_list_url_name))

    @action(description="publish all drafts", variant=ActionVariant.PRIMARY)
    def publish_all_drafts(self, request):
        updated = Post.objects.filter(status=Post.Status.DRAFT).update(status= Post.Status.PUBLISHED, updated_at=timezone.now())
        self.message_user(request, f"published drafts: {updated}", messages.SUCCESS)
        return redirect(reverse(post_list_url_name))

    @action(description="open comments of this post", url_path="post-comments")
    def open_comments(self, request, object_id):
        url = reverse("admin:blog_comment_changelist")+ f"?post_id_exact={object_id}"
        return redirect(url)

    @action(description="save and publish")
    def save_and_publish(self, request, obj):
        obj.status = Post.Status.PUBLISHED
        obj.save()
        return redirect(reverse(post_list_url_name))
        obj.save()