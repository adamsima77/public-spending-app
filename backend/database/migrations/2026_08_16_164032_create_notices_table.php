<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notices', function (Blueprint $table) {
            $table->id();
            $table->string('notice_id', 250);
            $table->unsignedSmallInteger('notice_version');
            $table->string('form_type', 32)->nullable();
            $table->string('notice_type', 32)->nullable();
            $table->string('legal_basis', 64)->nullable();
            $table->text('title')->nullable();
            $table->timestamp('issue_date')->nullable();
            $table->timestamp('published_at')->nullable();
            $table->boolean('is_latest')->default(true);
            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['notice_id', 'notice_version']);
            $table->index('notice_id');
            $table->index('published_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notices');
    }
};