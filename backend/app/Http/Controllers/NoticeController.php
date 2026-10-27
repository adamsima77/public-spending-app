<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\NoticeResource;
use App\Models\Notice;
use App\Services\NoticeService;

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
    public function show(Notice $notice)
    {
        return new NoticeResource($notice);
    }
}
