<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('notices', function (Blueprint $table) {
            $table->id();
            $table->string('notice_id', 250);              // BT-701-notice
            $table->unsignedSmallInteger('notice_version'); // BT-757-notice
            $table->string('form_type', 32)->nullable();    // BT-03-notice
            $table->string('notice_type', 32)->nullable();  // BT-02-notice 
            $table->string('legal_basis', 64)->nullable();  // BT-01-notice
            $table->text('title')->nullable();              // DL-Metadata-Order
            $table->timestamp('contract_conclusion_date')->nullable();
            $table->timestamp('issue_date')->nullable();
            $table->timestamps();
            $table->unique(['notice_id', 'notice_version']);
            $table->jsonb('extra_fields')->nullable();
            $table->timestamp('published_at')->nullable()->after('issue_date'); 
            $table->boolean('is_latest')->default(true)->after('published_at'); 
            $table->index('notice_id'); 
            $table->index('published_at'); 
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('notices');
    }
};