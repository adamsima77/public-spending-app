<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\NoticeService;
use App\Http\Resources\NoticeResource;
use Illuminate\Http\Response;
use App\Models\Notice;

class NoticeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeService $noticeService)
    {
        $notices = $noticeService->getNotices();
        return NoticeResource::collection($notices);  
    }

    /**
     * Display the specified resource.
     */
    public function show(Notice $notice, NoticeService $noticeService)
    {
        return new NoticeResource($notice);
    }
}
