"""
URL configuration for ProgramWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import accounts.views as accounts_views
import userinfos.views as userinfos_views
import news.views as news_views
import questions.views as questions_views
import answers.views as answers_views
import reviews.views as reviews_views
from django.conf import settings
from django.conf.urls.static import static
from userinfos.views import update_profile_img

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # -------- Accounts URLs --------
    path("", accounts_views.index, name="Index"),
    path("login/", accounts_views.login, name="Login"),
    path("logout/", accounts_views.logout, name="Logout"),
    path("register/", accounts_views.register, name="Register"),
    
    # -------- User Information URLs --------
    path("userinfo/", userinfos_views.userinfo, name="UserInfo"),
    path("userinfo/updateimg/", update_profile_img, name="UpdateProfileImg"),
    path("userinfo/questions/", userinfos_views.user_dashboard, name="UserinfoQuestions"),
    
    # -------- News URLs --------
    path("news/", news_views.news_list, name="NewsList"),
    path("news/<slug:slug>/", news_views.news_unit, name="NewsUnit"),

    # -------- Questions URLs --------
    path("questions/create/", questions_views.create_question, name="CreateQuestion"),
    path("questions/<int:question_id>/", questions_views.question_detail, name="QuestionDetail"),
    path("questions/<int:question_id>/<int:version>/", questions_views.question_version, name="QuestionDetailVersion"),
    path("questions/<int:question_id>/update/", questions_views.question_update, name="QuestionUpdate"),
    path("question/list/", questions_views.question_list, name="QuestionList"),

    # -------- Answers URLs --------
    path("answers/create/<int:question_id>/", answers_views.create_answer, name="CreateAnswer"),
    path("answers/submit/", answers_views.submit_answer, name="SubmitAnswer"),
    path("answers/debug/", answers_views.debug_answer, name="DebugAnswer"),

    # -------- Reviews URLs --------
    path("reviews/create/<int:question_id>/", reviews_views.create_review, name="CreateReview"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
