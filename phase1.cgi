#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use HTML::FillInForm;
use SFCON::Register;
use SFCON::Register_db;

my $c_not_fill = 'bgcolor="red"';

my $register = SFCON::Register->new;
my $cgi=CGI->new;
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
#1.cookieからCGISESSIDを探す
#2.cookieから取れなかったらurlパラメータを探す．
#3.どちらも取得できなかったらundef．
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page=HTML::Template->new(filename => 'phase1-tmpl.html');
my $form_out = HTML::FillInForm->new;
my $html_out;

#4.取得したセッションidが有効ならそのまま．無効なら別のidを発番．

if(defined $sid && $sid eq $session->id){
#cookieかurlパラメータから値を取得でき，かつ有効なid
	$input_page->param(ID => $sid);

	if($session->param('phase') ne '1-2' || $cgi->param('self') ne 'true') {
        # 申し込み画面初期表示
		$session->param('phase','1-2');
		$html_out = $form_out->fill(
			scalarref => \$input_page->output,
			target => "mailform",
			fobject => $session
		);
	} else {
        # 申し込み受付時チェック

		if ( _input_check($cgi, $input_page) ) {
            # 入力内容不備時 申込画面再表示
			$html_out = $form_out->fill(
				scalarref => \$input_page->output,
				target => "mailform",
				fobject => $cgi
			);
		} else {
            # 申し込み成功 
			$session->save_param($cgi);
			$html_out = $form_out->fill(
				scalarref => \$input_page->output,
				target => "mailform",
				fobject => $cgi
			);
			if($cgi->cookie('ID') eq  $session->id){
				print $cgi->redirect('./phase2.cgi');
			} else {
				print $cgi->redirect('./phase2.cgi?ID='. $sid);
			}
			exit;
		}
	}
	my $cookie_path = $ENV{SCRIPT_NAME};
	$cookie_path =~ s/[^\/]+$//g ;
	my $cookie = $cgi->cookie(-name => "ID", -value   => "$sid", -expires => "+3h", -path => "$cookie_path");

	print $cgi->header(-charset=>'UTF-8', -expires=>'now', -cookie=>$cookie);
	print "\n\n".$html_out;

}else{
    # セッションタイムアウトなど
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
	print $cgi->redirect('./error.html');
}
exit;

sub _input_check {
	my ($cgi, $input_page) = @_;
	my $input_check = 0;
	
# 主催者情報
    # 名前
	if($cgi->param('p1_name') eq ''){
		$input_page->param(C_P1_NAME => $c_not_fill);
		$input_check = 1;
	}
    # メールアドレス
	if($cgi->param('email') eq ''){
		$input_page->param(C_CO_EMAIL => $c_not_fill);
		$input_check = 1;
	}
    # 参加登録番号
	if($cgi->param('reg_num') eq ''){
		$input_page->param(C_CO_REG_NUMBER => $c_not_fill);
		$input_check = 1;
	}
    # 電話番号、FAX番号、携帯番号は省略可能

# 企画情報
    # 企画名称
	if($cgi->param('pg_name') eq ''){
		$input_page->param(C_CO_PG_NAME => $c_not_fill);
		$input_check = 1;
	}
    # 企画名称フリガナ
	if($cgi->param('pg_name_f') eq ''){
		$input_page->param(C_CO_PG_NAME_F => $c_not_fill);
		$input_check = 1;
	}
    # 企画種別
	if($cgi->param('pg_kind') eq ''){
		$input_page->param(C_CO_PG_KIND => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_kind') eq 'K-X1' && $cgi->param('pg_kind2') eq ''){
		$input_page->param(C_CO_PG_KIND => $c_not_fill);
		$input_check = 1;
	}
    # 希望場所
	if($cgi->param('pg_place') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_place') eq 'P-X1' && $cgi->param('pg_place2') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
    # 希望場所レイアウト
	if($cgi->param('pg_layout') eq '9' && $cgi->param('pg_layout2') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
    # 小ホールはシアターのみ
	if($cgi->param('pg_place') eq 'P-H1' && $cgi->param('pg_layout') ne '0'){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
    # 希望日時
	if($cgi->param('pg_time') eq ''){
		$input_page->param(C_CO_PG_TIME => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_time') eq 'T-X1' && $cgi->param('pg_time2') eq ''){
		$input_page->param(C_CO_PG_TIME => $c_not_fill);
		$input_check = 1;
	}
    # 希望コマ数
	if($cgi->param('pg_koma') eq ''){
		$input_page->param(C_CO_PG_KOMA => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_koma') eq 'TK-X1' && $cgi->param('pg_koma2') eq ''){
		$input_page->param(C_CO_PG_KOMA => $c_not_fill);
		$input_check = 1;
	}
    # 予想参加者
	if($cgi->param('pg_ninzu') eq ''){
		$input_page->param(C_CO_PG_NINZU => $c_not_fill);
		$input_check = 1;
	}
    # 内容説明
	if($cgi->param('pg_naiyou') eq '' || $cgi->param('pg_naiyou_k') eq ''){
		$input_page->param(C_CO_PG_NAIYOU => $c_not_fill);
		$input_check = 1;
	}
    # リアルタイム公開
	if($cgi->param('pg_kiroku_kb') eq ''){
		$input_page->param(C_CO_PG_KIROKU_KB => $c_not_fill);
		$input_check = 1;
	}
    # 事後公開
	if($cgi->param('pg_kiroku_ka') eq ''){
		$input_page->param(C_CO_PG_KIROKU_KA => $c_not_fill);
		$input_check = 1;
	}
    # 使用機材
    if (   ( $cgi->param('mic') && $cgi->param('miccnt') <= 0 )
        || ( $cgi->param('mic2') && $cgi->param('mic2cnt') <= 0 )
       ) {
		$input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		$input_check = 1;
	}
    if ( $cgi->param('fc_vid') eq '0' ) {
        if (   ( $cgi->param('av-v') eq '' )
            || (( $cgi->param('av-v') eq 'other' ) &&
                ( $cgi->param('av-v_velse') eq '')    )
           ) {
		    $input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		    $input_check = 1;
        }
        if (   ( $cgi->param('av-a') eq '' )
            || (( $cgi->param('av-a') eq 'other' ) &&
                ( $cgi->param('av-a_velse') eq '')    )
           ) {
		    $input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		    $input_check = 1;
        }
	}
    if ( $cgi->param('fc_pc') eq '0' ) {
        if (   ( $cgi->param('pc-v') eq '' )
            || (( $cgi->param('pc-v') eq 'other' ) &&
                ( $cgi->param('pc-v_velse') eq '')    )
           ) {
		    $input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		    $input_check = 1;
        }
        if (   ( $cgi->param('pc-a') eq '' )
            || (( $cgi->param('pc-a') eq 'other' ) &&
                ( $cgi->param('pc-a_velse') eq '')    )
           ) {
		    $input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		    $input_check = 1;
        }
        if (   ( $cgi->param('lan') eq '' )
            || (( $cgi->param('lan') eq 'other' ) &&
                ( $cgi->param('pc-l_velse') eq '')   )
            || (( $cgi->param('lan') ne 'none' )  &&
                ( $cgi->param('lanreason') eq '' )   )
           ) {
		    $input_page->param(C_CO_PG_KIZAI => $c_not_fill);
		    $input_check = 1;
        }
	}
    # 企画を立てるのは
	if($cgi->param('pg_enquete') eq ''){
		$input_page->param(C_CO_PG_ENQUETE => $c_not_fill);
		$input_check = 1;
	}

    # 出演者情報
    my $ppcnt;
	for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {	# CONST: 出演者の最大値
        my $ppname      = 'pp' . $ppcnt . '_name';
        my $ppname_f    = 'pp' . $ppcnt . '_name_f';
        my $ppcon       = 'pp' . $ppcnt . '_con';
        my $ppgrq       = 'pp' . $ppcnt . '_grq';
        my $CCOPG       = 'C_CO_PG_GUEST' . $ppcnt;
	    if ($cgi->param($ppname) ne '' || $cgi->param($ppname_f) ne ''){
		    if ($cgi->param($ppname) eq '' || $cgi->param($ppname_f) eq '' ||
                $cgi->param($ppcon)  eq '' || $cgi->param($ppgrq) eq ''){
			    $input_page->param($CCOPG => $c_not_fill);
			    $input_check = 1;
		    }
	    }
    }

	return($input_check);
}

#end
